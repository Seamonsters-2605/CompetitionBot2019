import math
import wpilib
import ctre
import navx
import seamonsters as sea
import drivetrain
import dashboard
import grabber
from buttons import Buttons
import auto_scheduler
import auto_vision
import auto_actions
import auto_grabber
import coordinates
from networktables import NetworkTables
import climber

OPTICAL_SENSOR_THRESHOLD = 0.5 # volts

class CompetitionBot2019(sea.GeneratorBot):

    def robotInit(self):
        # DEVICES

        self.joystick = wpilib.Joystick(0)
        self.buttonBoard = wpilib.Joystick(1)

        self.opticalSensors = [
            wpilib.AnalogInput(0), wpilib.AnalogInput(1),
            wpilib.AnalogInput(2), wpilib.AnalogInput(3)]

        ahrs = navx.AHRS.create_spi()

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.vision = NetworkTables.getTable('limelight')

        # SUBSYSTEMS

        self.superDrive = drivetrain.initDrivetrain()
        self.superDrive.gear = None
        self.multiDrive = sea.MultiDrive(self.superDrive)

        self.grabberArm = grabber.GrabberArm()
        self.climber = climber.Climber()

        # HELPER OBJECTS

        self.pathFollower = sea.PathFollower(self.superDrive, ahrs)
        startPosition = coordinates.startCenter.inQuadrant(1)
        self.pathFollower.setPosition(startPosition.x, startPosition.y, startPosition.orientation)

        self.autoScheduler = auto_scheduler.AutoScheduler()
        self.autoScheduler.updateCallback = self.updateScheduler
        self.autoScheduler.idleFunction = self.autoIdle

        self.timingMonitor = sea.TimingMonitor()

        # MANUAL DRIVE STATE

        self.driveVoltage = False
        self.manualGear = None
        self.fieldOriented = True
        self.holdGear = False

        self.manualAuxModeMachine = sea.StateMachine()
        self.auxDisabledState = sea.State(self.auxDisabledMode)
        self.defenseState = sea.State(self.manualDefenseMode)
        self.hatchState = sea.State(self.manualHatchMode)
        self.cargoState = sea.State(self.manualCargoMode)
        self.climbState = sea.State(self.manualClimbMode)

        self.controlModeMachine = sea.StateMachine()
        self.autoState = sea.State(self.autoScheduler.runSchedule)
        self.manualState = sea.State(lambda: sea.parallel(
            self.manualDriving(), self.manualAuxModeMachine.updateGenerator()))

        # DASHBOARD

        self.genericAutoActions = auto_actions.createGenericAutoActions(
            self.pathFollower, self.grabberArm, self.vision)

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)

        #wpilib.CameraServer.launch('camera.py:main')

    def resetPositions(self):
        for wheel in self.superDrive.wheels:
            wheel.resetPosition()

    def teleop(self):
        self.manualMode()
        yield from self.mainGenerator()
    
    def autonomous(self):
        self.grabberArm.resetAllSensors()
        yield from self.homeAllSwerveWheels()

        self.autoMode()
        yield from self.mainGenerator()

    def test(self):
        self.grabberArm.disableAllMotors()
        yield from sea.parallel(
            self.dashboardUpdateGenerator(),
            self.timingMonitor.updateGenerator()
        )

    def mainGenerator(self):
        self.resetPositions()
        yield from sea.parallel(
            self.controlModeMachine.updateGenerator(),
            self.dashboardUpdateGenerator(),
            self.timingMonitor.updateGenerator()
        )

    def autoIdle(self):
        # runs in auto mode when no Actions are running
        self.pathFollower.updateRobotPosition()
        self.superDrive.drive(0, 0, 0)

    def dashboardUpdateGenerator(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            v = None
            if self.app is not None:
                v = self.app.doEvents()
            self.updateDashboardLabels()
            yield v

    def getThrottlePos(self):
        throttle = sea.deadZone(-self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_THROTTLE))
        if throttle > 0.5:
            return 3
        elif throttle < -0.5:
            return 1
        else:
            return 2

    def manualDriving(self):
        self.manualMediumGear()
        self.manualAuxModeMachine.replace(self.auxDisabledState)

        self.resetPositions()
        
        alignAngle = None

        # clear joystick events
        for i in range(1,13):
            self.joystick.getRawButtonPressed(i)
            self.joystick.getRawButtonReleased(i)

        while True:
            # BUTTON BOARD

            if self.buttonBoard.getRawButtonPressed(3):
                self.manualSlowGear()
            if self.buttonBoard.getRawButtonPressed(4):
                self.manualMediumGear()
            if self.buttonBoard.getRawButtonPressed(5):
                self.manualFastGear()

            # DRIVING

            self.pathFollower.updateRobotPosition()

            if self.joystick.getRawButtonPressed(4):
                yield sea.AddParallelSignal(self.manualVisionAlign())

            x = sea.deadZone(self.joystick.getX())
            y = sea.deadZone(self.joystick.getY())
            mag = math.hypot(x * (1 - 0.5*y**2) ** 0.5,y * (1 - 0.5*x**2) ** 0.5)
            mag *= self.manualGear.moveScale

            direction = -self.joystick.getDirectionRadians() + math.pi/2

            if self.fieldOriented and not self.joystick.getRawButton(4):
                direction -= self.pathFollower.robotAngle + math.pi/2
            
            turn = -sea.deadZone(self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_TWIST)) \
                - 0.5 * sea.deadZone(self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_LEVER))
            if turn != 0:
                alignAngle = None
            turn *= self.manualGear.turnScale # maximum radians per second

            if not self.joystick.getPOV() == -1:
                pov = self.joystick.getPOV()
                if pov == 45:
                    pov = 30
                elif pov == 135:
                    pov = 150
                elif pov == 225:
                    pov = 210
                elif pov == 315:
                    pov = 330
                alignAngle = -math.radians(pov) - math.pi / 2
            if alignAngle is not None:
                aDiff = sea.circleDistance(alignAngle, self.pathFollower.robotAngle)
                turn = sea.feedbackLoopScale(-aDiff, 25, 2, drivetrain.mediumPositionGear.turnScale)

            if not self.holdGear:
                self.manualGear.applyGear(self.superDrive)

            if self.buttonBoard.getRawButton(1) or wpilib.RobotController.isBrownedOut():
                alignAngle = None
                self.superDrive.disable()
            else:
                self.multiDrive.drive(mag, direction, turn)
            self.multiDrive.update()

            yield

    def manualVisionAlign(self):
        self.holdGear = True
        yield from sea.parallel(
            auto_vision.driveIntoVisionTarget(
                self.multiDrive, self.vision, self.superDrive),
            sea.stopAllWhenDone(sea.whileButtonPressed(self.joystick, 4)))
        self.manualMediumGear()
        self.holdGear = False

    def elevatorControl(self):
        self.grabberArm.elevatorSlide(-self.buttonBoard.getY() * 0.5)

    def auxDisabledMode(self):
        if self.app is not None:
            self.app.auxModeGroup.highlight("disabled")
        self.grabberArm.disableAllMotors()
        yield from sea.forever()

    def manualDefenseMode(self):
        if self.app is not None:
            self.app.auxModeGroup.highlight("defense")
        self.grabberArm.stopIntake()
        self.grabberArm.setInnerPiston(False)
        self.grabberArm.setOuterPiston(False)
        self.grabberArm.elevatorToZero()
        while True:
            self.grabberArm.clawBack()
            yield

    def manualCargoMode(self):
        if self.app is not None:
            self.app.auxModeGroup.highlight("cargo")
        self.grabberArm.setInnerPiston(False)
        self.grabberArm.setOuterPiston(False)
        self.grabberArm.elevatorSlide(0)
        while True:
            if self.joystick.getRawButton(8):
                self.grabberArm.elevatorCargoPosition(self.getThrottlePos())
            elif self.joystick.getRawButton(1):
                self.grabberArm.clawOpen()
                self.grabberArm.elevatorFloor()
            else:
                self.grabberArm.clawClosed()
                self.elevatorControl()

            if self.joystick.getRawButton(2):
                self.grabberArm.eject()
            if self.joystick.getRawButtonReleased(2):
                self.grabberArm.stopIntake()

            try:
                yield
            except:
                self.grabberArm.disableAllMotors()
                return

    def manualHatchMode(self):
        if self.app is not None:
            self.app.auxModeGroup.highlight("hatch")
        self.grabberArm.stopIntake()
        self.grabberArm.elevatorSlide(0)
        self.grabberArm.setInnerPiston(False)
        self.joystick.getRawButtonPressed(1)
        while True:
            self.grabberArm.clawHatch()
            if self.joystick.getRawButton(2):
                self.grabberArm.setOuterPiston(True)
            if self.joystick.getRawButton(10):
                self.grabberArm.setOuterPiston(False)

            if self.joystick.getRawButtonPressed(1):
                self.holdGear = True
                yield from auto_grabber.pickUpHatch(
                    self.multiDrive, self.grabberArm, self.superDrive)
                self.holdGear = False

            if self.joystick.getRawButton(8):
                self.grabberArm.elevatorHatchPosition(self.getThrottlePos())
            else:
                self.elevatorControl()

            try:
                yield
            except:
                self.grabberArm.disableAllMotors()
                return

    def manualClimbMode(self):
        if self.app is not None:
            self.app.auxModeGroup.highlight("climb")
        while True:
            self.climber.climb(-self.buttonBoard.getY())
            yield

    def updateDashboardLabels(self):
        pass

    def updateScheduler(self):
        if self.app is not None:
            self.app.updateSchedulerFlag = True

    # STATE CHANGE
    # these functions should be called rather than setting state variables directly
    # they will also update the dashboard

    def autoMode(self):
        self.controlModeMachine.replace(self.autoState)
        self.updateScheduler()
        if self.app is not None:
            self.app.controlModeGroup.highlight("auto")

    def manualMode(self):
        self.controlModeMachine.replace(self.manualState)
        self.updateScheduler()
        if self.app is not None:
            self.app.controlModeGroup.highlight("manual")

    def manualSlowGear(self):
        if self.driveVoltage:
            self.manualGear = drivetrain.slowVoltageGear
        else:
            self.manualGear = drivetrain.slowPositionGear
        self.setFieldOriented(False)
        if self.app is not None:
            self.app.gearGroup.highlight("slow")

    def manualMediumGear(self):
        if self.driveVoltage:
            self.manualGear = drivetrain.mediumVoltageGear
        else:
            self.manualGear = drivetrain.mediumPositionGear
        self.setFieldOriented(True)
        if self.app is not None:
            self.app.gearGroup.highlight("medium")

    def manualFastGear(self):
        if self.driveVoltage:
            self.manualGear = drivetrain.fastVoltageGear
        else:
            self.manualGear = drivetrain.fastPositionGear
        self.setFieldOriented(True)
        if self.app is not None:
            self.app.gearGroup.highlight("fast")

    def driveVoltageMode(self):
        self.driveVoltage = True
        self.manualMediumGear()
        if self.app is not None:
            self.app.voltageModeGroup.highlight(True)
        
    def drivePositionMode(self):
        self.driveVoltage = False
        self.manualMediumGear()
        if self.app is not None:
            self.app.voltageModeGroup.highlight(False)

    def setFieldOriented(self, enabled):
        self.fieldOriented = enabled
        if self.app is not None:
            self.app.fieldOrientedGroup.highlight(enabled)

    # TEST FUNCTIONS

    def logOpticalSensors(self):
        while True:
            print("%.3f %.3f %.3f %.3f" %
                (self.opticalSensors[0].getVoltage(), self.opticalSensors[1].getVoltage(),
                 self.opticalSensors[2].getVoltage(), self.opticalSensors[3].getVoltage()))
            yield

    def logElevator(self):
        while True:
            print(self.grabberArm.safeForArmsToClose(), self.grabberArm.safeForArmsToGoBack())
            yield

    def homeSwerveWheel(self, name, swerveWheel, sensor, angle):
        swerveWheel.zeroSteering()
        motor = swerveWheel.steerMotor
        initialPos = motor.getSelectedSensorPosition(0)
        motor.set(ctre.ControlMode.PercentOutput, -0.2)
        i = 0
        while True:
            i += 1
            if i == 150:
                print("Couldn't home wheel!")
                motor.set(ctre.ControlMode.Position, initialPos)
                break
            voltage = sensor.getVoltage()
            #print(voltage)
            if voltage < OPTICAL_SENSOR_THRESHOLD:
                motor.set(ctre.ControlMode.PercentOutput, 0)
                break
            yield
        print(name, math.degrees(swerveWheel._getCurrentSteeringAngle()))
        swerveWheel.zeroSteering(angle)

    def homeAllSwerveWheels(self):
        yield from sea.parallel(
            self.homeSwerveWheel('A', self.superDrive.wheels[0], self.opticalSensors[0],
                math.radians(-180 + 82.589)),
            self.homeSwerveWheel('B', self.superDrive.wheels[1], self.opticalSensors[1],
                math.radians(20.759)),
            self.homeSwerveWheel('C', self.superDrive.wheels[2], self.opticalSensors[2],
                math.radians(-180 + 21.875)),
            self.homeSwerveWheel('D', self.superDrive.wheels[3], self.opticalSensors[3],
                math.radians(90 + 58.705)))


    # dashboard callbacks

    @sea.queuedDashboardEvent
    def c_toggleVoltage(self, button):
        if self.driveVoltage:
            self.drivePositionMode()
        else:
            self.driveVoltageMode()

    def c_toggleFieldOriented(self, button):
        self.setFieldOriented(not self.fieldOriented)

    def c_slowGear(self, button):
        self.manualSlowGear()

    def c_mediumGear(self, button):
        self.manualMediumGear()

    def c_fastGear(self, button):
        self.manualFastGear()

    @sea.queuedDashboardEvent
    def c_wheelButtonClicked(self, button):
        button.controller.clicked()

    @sea.queuedDashboardEvent
    def c_manualMode(self, button):
        self.manualMode()

    @sea.queuedDashboardEvent
    def c_autoMode(self, button):
        self.autoMode()
    
    @sea.queuedDashboardEvent
    def c_defenseMode(self, button):
        self.manualAuxModeMachine.replace(self.defenseState)

    @sea.queuedDashboardEvent
    def c_cargoMode(self, button):
        self.manualAuxModeMachine.replace(self.cargoState)
    
    @sea.queuedDashboardEvent
    def c_hatchMode(self, button):
        self.manualAuxModeMachine.replace(self.hatchState)

    @sea.queuedDashboardEvent
    def c_climbMode(self, button):
        self.manualAuxModeMachine.replace(self.climbState)

    # TESTING

    @sea.queuedDashboardEvent
    def c_startCompressor(self, button):
        self.grabberArm.startCompressor()

    @sea.queuedDashboardEvent
    def c_stopCompressor(self, button):
        self.grabberArm.stopCompressor()

    @sea.queuedDashboardEvent
    def c_wheelsToZero(self, button):
        for wheel in self.superDrive.wheels:
            wheel._setSteering(0)

    @sea.queuedDashboardEvent
    def c_setSwerveZero(self, button):
        for wheel in self.superDrive.wheels:
            wheel.zeroSteering()

    @sea.queuedDashboardEvent
    def c_homeSwerveWheels(self, button):
        return sea.AddParallelSignal(self.homeAllSwerveWheels())

    @sea.queuedDashboardEvent
    def c_logOpticalSensors(self, button):
        return sea.AddParallelSignal(self.logOpticalSensors())

    @sea.queuedDashboardEvent
    def c_logElevator(self, button):
        return sea.AddParallelSignal(self.logElevator())

    @sea.queuedDashboardEvent
    def c_resetClaw(self, button):
        self.grabberArm.resetAllSensors()


if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)