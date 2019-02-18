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
import coordinates
from networktables import NetworkTables
import climber

DISABLE_MOTORS_TIME = 50 # iterations
OPTICAL_SENSOR_THRESHOLD = 0.5 # volts

class CompetitionBot2019(sea.GeneratorBot):

    def robotInit(self):
        self.grabberArm = grabber.GrabberArm()
        self.grabberArm.stopCompressor()
        self.climber = climber.Climber()

        self.joystick = wpilib.Joystick(0)

        self.superDrive = drivetrain.initDrivetrain()
        self.superDrive.gear = None
        self.manualGear = None
        self.headless_mode = True

        self.opticalSensors = [
            wpilib.AnalogInput(0), wpilib.AnalogInput(1),
            wpilib.AnalogInput(2), wpilib.AnalogInput(3)]
        
        self.ahrs = navx.AHRS.create_spi()
        self.pathFollower = sea.PathFollower(self.superDrive, self.ahrs)
        startPosition = coordinates.startCenter.inQuadrant(1)
        self.pathFollower.setPosition(startPosition.x, startPosition.y, startPosition.orientation)

        self.joystick = wpilib.Joystick(0)

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.autoScheduler = auto_scheduler.AutoScheduler()
        self.autoScheduler.updateCallback = self.updateScheduler
        self.autoScheduler.idleFunction = self.autoIdle
        self.controlModeMachine = sea.StateMachine()
        self.autoState = sea.State(self.autoScheduler.runSchedule)
        self.manualState = sea.State(self.joystickControl)

        self.timingMonitor = sea.TimingMonitor()

        self.vision = NetworkTables.getTable('limelight')

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)
        self.lbl_current = "no"
        self.lbl_encoder = 'no'

        self.cargoMode = False
        self.defenseMode = True
        self.hatchMode = False

    def updateScheduler(self):
        if self.app is not None:
            self.app.updateSchedulerFlag = True

    def resetPositions(self):
        for wheel in self.superDrive.wheels:
            wheel.resetPosition()

    def test(self):
        # while True:
        #     print("%.3f %.3f %.3f %.3f" % (self.opticalSensors[0].getVoltage(),
        #                                    self.opticalSensors[1].getVoltage(),
        #                                    self.opticalSensors[2].getVoltage(),
        #                                    self.opticalSensors[3].getVoltage()))
        #     yield
        yield from sea.parallel(
            self.homeSwerveWheel(0, self.superDrive.wheels[0], self.opticalSensors[0],
                math.radians(-180 + 82.589)),
            self.homeSwerveWheel(1, self.superDrive.wheels[1], self.opticalSensors[1],
                math.radians(20.759)),
            self.homeSwerveWheel(2, self.superDrive.wheels[2], self.opticalSensors[2],
                math.radians(-180 + 21.875)),
            self.homeSwerveWheel(3, self.superDrive.wheels[3], self.opticalSensors[3],
                math.radians(90 + 58.705)))

    def homeSwerveWheel(self, num, swerveWheel, sensor, angle):
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
                motor.set(0)
                break
            yield
        print(num, math.degrees(swerveWheel._getCurrentSteeringAngle()))
        swerveWheel.zeroSteering(angle)
        swerveWheel._setSteering(0)


    def teleop(self):
        self.manualMode()
        self.grabberArm.resetAllSensors()
        yield from self.mainGenerator()
    
    def autonomous(self):
        self.autoMode()
        yield from self.mainGenerator()

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

    def autoMode(self):
        self.controlModeMachine.replace(self.autoState)
        self.updateScheduler()

    def manualMode(self):
        self.controlModeMachine.replace(self.manualState)
        self.updateScheduler()

    def dashboardUpdateGenerator(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            if self.app is not None:
                self.app.doEvents()
            self.updateDashboardLabels()
            yield

    def joystickControl(self):
        self.manualGear = drivetrain.fastPositionGear
        self.setHeadless(True)
        self.resetPositions()
        currentMode = None

        self.joystick.getRawButtonPressed(1)
        self.joystick.getRawButtonPressed(11)
        self.joystick.getRawButtonPressed(12)

        while True:
            # GRABBER

            throttle = sea.deadZone(-self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_THROTTLE))
            if throttle > 0.5:
                throttlePos = 3
            elif throttle < -0.5:
                throttlePos = 1
            else:
                throttlePos = 2

            # Cargo Mode
            if self.cargoMode:
                if currentMode != "cargo":
                    currentMode = "cargo"
                    self.grabberArm.setInnerPiston(False)
                    self.grabberArm.setOuterPiston(False)
                    self.grabberArm.clawClosed()
                               
                if self.joystick.getRawButtonPressed(1):
                    self.grabberArm.clawOpen()
                if self.joystick.getRawButtonReleased(1):
                    self.grabberArm.clawClosed()
                    def releasedAction():
                        self.grabberArm.intake()
                        yield from sea.wait(30)
                        self.grabberArm.stopIntake()
                    yield sea.AddParallelSignal(releasedAction())
                if self.joystick.getRawButton(2):
                    self.grabberArm.eject()
                if self.joystick.getRawButtonReleased(2):
                    self.grabberArm.stopIntake()

                self.grabberArm.elevatorCargoPosition(throttlePos)

            elif self.hatchMode:
                if currentMode != "hatch":
                    currentMode = "hatch"
                    self.grabberArm.clawHatch()
                    self.grabberArm.stopIntake()
                
                if self.joystick.getRawButton(2):
                    self.grabberArm.setInnerPiston(False)
                    self.grabberArm.setOuterPiston(True)
                if self.joystick.getRawButton(1):
                    self.grabberArm.setInnerPiston(True)
                    self.grabberArm.setOuterPiston(False)
                if self.joystick.getRawButton(10):
                    self.grabberArm.setInnerPiston(False)
                    self.grabberArm.setOuterPiston(False)

                self.grabberArm.elevatorHatchPosition(throttlePos)

            elif self.defenseMode:
                if currentMode != "defense":
                    currentMode = "defense"
                    self.grabberArm.clawBack()
                    self.grabberArm.stopIntake()
                    self.grabberArm.setInnerPiston(False)
                    self.grabberArm.setOuterPiston(False)
                    self.grabberArm.elevatorSlide(0)

            #self.grabberArm.elevatorSlide(throttle)

            # CLIMBER

            if self.joystick.getRawButtonPressed(11):
                self.climber.climb(1)
            if self.joystick.getRawButtonReleased(11):
                self.climber.climb(0)
            if self.joystick.getRawButtonPressed(12):
                self.climber.climb(-1)
            if self.joystick.getRawButtonReleased(12):
                self.climber.climb(0)

            # DRIVING

            # if self.joystick.getRawButton(11):
            #     self.manualGear = drivetrain.slowPositionGear
            #     self.setHeadless(False)
            # if self.joystick.getRawButton(12):
            #     self.manualGear = drivetrain.fastPositionGear
            #     self.setHeadless(True)

            self.pathFollower.updateRobotPosition()

            if self.joystick.getRawButton(4):
                yield from sea.parallel(auto_vision.strafeAlign(self.superDrive, self.vision),
                    sea.stopAllWhenDone(sea.whileButtonPressed(self.joystick, 4)))

            x = sea.deadZone(self.joystick.getX())
            y = sea.deadZone(self.joystick.getY())
            mag = math.hypot(x * (1 - 0.5*y**2) ** 0.5,y * (1 - 0.5*x**2) ** 0.5)
            mag *= self.manualGear.moveScale

            direction = -self.joystick.getDirectionRadians() + math.pi/2

            if self.headless_mode:
                direction -= self.pathFollower.robotAngle + math.pi/2
            
            turn = -sea.deadZone(self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_TWIST)) \
                - 0.5 * sea.deadZone(self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_LEVER))
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
                aDiff = sea.circleDistance(-math.radians(pov) - math.pi/2, self.pathFollower.robotAngle)
                turn = sea.feedbackLoopScale(-aDiff, 10, 2, drivetrain.mediumPositionGear.turnScale)

            if self.manualGear.applyGear(self.superDrive):
                if self.app is not None:
                    self.app.driveGearLbl.set_text("Gear: " + str(self.manualGear))

            if self.joystick.getRawButton(9) or wpilib.RobotController.isBrownedOut():
                self.superDrive.disable()
            else:
                self.superDrive.drive(mag, direction, turn)

            yield

    def updateDashboardLabels(self):
        #self.lbl_current = str(self.pdp.getTotalCurrent())
        self.lbl_current = "no"
        self.lbl_encoder = ''
        for wheel in self.superDrive.wheels:
            self.lbl_encoder += '%.3f ' % math.degrees(wheel.getRealDirection())

    def setHeadless(self, on):
        self.headless_mode = on
        if self.app is not None:
            self.app.fieldOrientedLbl.set_text("Field oriented: " + ("On" if on else "Off"))

    # dashboard callbacks

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
    def c_slowVoltageGear(self, button):
        self.manualGear = drivetrain.slowVoltageGear

    @sea.queuedDashboardEvent
    def c_mediumVoltageGear(self, button):
        self.manualGear = drivetrain.mediumVoltageGear

    @sea.queuedDashboardEvent
    def c_fastVoltageGear(self, button):
        self.manualGear = drivetrain.fastVoltageGear

    @sea.queuedDashboardEvent
    def c_slowPositionGear(self, button):
        self.manualGear = drivetrain.slowPositionGear

    @sea.queuedDashboardEvent
    def c_mediumPositionGear(self, button):
        self.manualGear = drivetrain.mediumPositionGear

    @sea.queuedDashboardEvent
    def c_fastPositionGear(self, button):
        self.manualGear = drivetrain.fastPositionGear

    @sea.queuedDashboardEvent
    def c_disableWheel(self, button):
        self.superDrive.wheels[button.wheelNum - 1].angledWheel.driveMode = ctre.ControlMode.Disabled
        self.app.switchDeadWheelText(button)

    @sea.queuedDashboardEvent
    def c_manualMode(self, button):
        self.manualMode()

    @sea.queuedDashboardEvent
    def c_autoMode(self, button):
        self.autoMode()
    
    @sea.queuedDashboardEvent
    def c_defenseMode(self, button):
        self.defenseMode = True
        self.hatchMode = False
        self.cargoMode = False

    @sea.queuedDashboardEvent
    def c_cargoMode(self, button):
        self.defenseMode = False
        self.hatchMode = False
        self.cargoMode = True
    
    @sea.queuedDashboardEvent
    def c_hatchMode(self, button):
        self.defenseMode = False
        self.hatchMode = True
        self.cargoMode = False

if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)