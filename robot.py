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
import auto_actions
import coordinates
from networktables import NetworkTables

DISABLE_MOTORS_TIME = 50 # iterations

class CompetitionBot2019(sea.GeneratorBot):

    def robotInit(self):
        self.grabberArm = grabber.GrabberArm()

        self.joystick = wpilib.Joystick(0)

        self.superDrive = drivetrain.initDrivetrain()
        self.drivegear = None
        self.headless_mode = True
        
        self.ahrs = navx.AHRS.create_spi()
        self.pathFollower = sea.PathFollower(self.superDrive, self.ahrs)

        self.joystick = wpilib.Joystick(0)

        self.pdp = wpilib.PowerDistributionPanel(50)
        self.testDIO = wpilib.DigitalInput(0)

        self.autoScheduler = auto_scheduler.AutoScheduler()
        self.autoScheduler.updateCallback = self.updateScheduler

        self.timingMonitor = sea.TimingMonitor()

        self.vision = NetworkTables.getTable('limelight')

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)

    def updateScheduler(self):
        if self.app is not None:
            self.app.updateScheduler()

    def resetPositions(self):
        for wheel in self.superDrive.wheels:
            wheel.resetPosition()

    def setGear(self, gear):
        if gear == self.drivegear:
            return
        self.drivegear = gear
        for wheel in self.superDrive.wheels:
            wheel.angledWheel.driveMode = gear.mode
            wheelMotor = wheel.angledWheel.motor
            wheelMotor.config_kP(0, self.drivegear.p, 0)
            wheelMotor.config_kI(0, self.drivegear.i, 0)
            wheelMotor.config_kD(0, self.drivegear.d, 0)
            wheelMotor.config_kF(0, self.drivegear.f, 0)
        if self.app is not None:
            self.app.driveGearLbl.set_text("Gear: " + str(gear))

    def disableMotors(self):
        for wheel in self.superDrive.wheels:
            wheel.angledWheel.driveMode = ctre.ControlMode.Disabled

    def enableMotors(self):
        for wheel in self.superDrive.wheels:
            wheel.angledWheel.driveMode = self.drivegear.mode

    def teleop(self):
        self.setGear(drivetrain.fastPositionGear)
        self.resetPositions()
        self.pathFollower.setPosition(0, 0, 0)
        yield from sea.parallel(self.joystickControl(),
            self.basicUpdateLoop(), self.timingMonitor.updateGenerator())
    
    def autonomous(self):
        self.setGear(drivetrain.mediumPositionGear)
        self.resetPositions()
        self.pathFollower.setPosition(0, 0, 0)
        self.superDrive.drive(0,0,0)
        yield from sea.parallel(self.autoScheduler.updateGenerator(),
            self.basicUpdateLoop(), self.timingMonitor.updateGenerator())

    def basicUpdateLoop(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            if self.app is not None:
                self.app.doEvents()
            self.updateDashboardLabels()
            yield

    def joystickControl(self):
        self.setHeadless(True)
        stoppedTime = 0

        while True:
            # GRABBER

            if self.joystick.getRawButton(1):
                self.grabberArm.grabBall()
                self.grabberArm.setInnerPiston(False)
                self.grabberArm.setOuterPiston(False)
            elif self.joystick.getRawButton(2):
                self.grabberArm.eject()
                self.grabberArm.setInnerPiston(False)
                self.grabberArm.setOuterPiston(False)
            else:
                self.grabberArm.stopIntake()

            if self.joystick.getRawButton(4):
                self.grabberArm.clawOpen()
                self.grabberArm.setInnerPiston(False)
                self.grabberArm.setOuterPiston(False)
            if self.joystick.getRawButton(3):
                self.grabberArm.clawBack()
                self.grabberArm.setInnerPiston(False)
                self.grabberArm.setOuterPiston(False)

            if self.joystick.getRawButton(5):
                self.grabberArm.setInnerPiston(True)
                self.grabberArm.setOuterPiston(False)
                self.grabberArm.clawHatch()
            elif self.joystick.getRawButton(6):
                self.grabberArm.setInnerPiston(False)
                self.grabberArm.setOuterPiston(True)
                self.grabberArm.clawHatch()
            elif self.joystick.getRawButton(7):
                self.grabberArm.setInnerPiston(False)
                self.grabberArm.setOuterPiston(False)
                self.grabberArm.clawHatch()

            self.grabberArm.slide(-self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_THROTTLE))

            # DRIVING

            if self.joystick.getRawButton(11):
                self.setGear(drivetrain.slowPositionGear)
                self.setHeadless(False)
            if self.joystick.getRawButton(12):
                self.setGear(drivetrain.fastPositionGear)
                self.setHeadless(True)

            self.pathFollower.updateRobotPosition()

            x = self.joystick.getX()
            y = self.joystick.getY()
            mag = sea.deadZone(math.hypot(x * (1 - 0.5*y**2) ** 0.5,y * (1 - 0.5*x**2) ** 0.5))
            mag *= self.drivegear.moveScale

            direction = -self.joystick.getDirectionRadians() + math.pi/2

            if self.headless_mode:
                direction -= self.pathFollower.robotAngle
            
            turn = -sea.deadZone(self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_TWIST)
                + 0.5 * self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_LEVER))
            turn *= self.drivegear.turnScale # maximum radians per second

            if not self.joystick.getPOV() == -1:
                aDiff = sea.circleDistance(-math.radians(self.joystick.getPOV()) + math.pi, self.pathFollower.robotAngle)
                turn = aDiff / 0.1 # seconds
                targetAVel = drivetrain.fastPositionGear.turnScale
                if turn > targetAVel:
                    turn = targetAVel
                elif turn < -targetAVel:
                    turn = -targetAVel

            if mag == 0 and turn == 0:
                stoppedTime += 1
            else:
                stoppedTime = 0
            if self.joystick.getRawButton(9):
                stoppedTime = DISABLE_MOTORS_TIME

            if stoppedTime >= DISABLE_MOTORS_TIME:
                self.disableMotors()
                self.superDrive.drive(0, 0, 0)
            else:
                self.enableMotors()
                self.superDrive.drive(mag, direction, turn)

            yield

    def updateDashboardLabels(self):
        if self.app != None:
            self.app.updateRobotPosition(
                self.pathFollower.robotX, self.pathFollower.robotY,
                self.pathFollower.robotAngle)
            self.app.realTimeRatioLbl.set_text(
                '%.3f' % (self.timingMonitor.realTimeRatio,))
            self.app.currentLbl.set_text(str(self.pdp.getTotalCurrent()))

            encoderString = ''
            for wheel in self.superDrive.wheels:
                encoderString += '%.3f ' % math.degrees(wheel.getRealDirection())
            self.app.encoderLbl.set_text(encoderString)

            self.app.updateBrokenEncoderButton(self)

    def toggleAutoScheduler(self):
        if self.autoScheduler.isPaused():
            self.autoScheduler.unpause()
        else:
            self.autoScheduler.pause()

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
    def c_addDriveToPointAction(self, button):
        speed = float(self.app.speedInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createDriveToPointAction(
                self.pathFollower, self.app.selectedCoord, speed))
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_addNavigateAction(self, button):
        coord = self.app.selectedCoord
        waypoints = coordinates.findWaypoints(coord,
            self.pathFollower.robotX, self.pathFollower.robotY, self.pathFollower.robotAngle)
        speed = float(self.app.speedInput.get_value())
        for pt in waypoints:
            action = auto_actions.createDriveToPointAction(self.pathFollower, pt, speed)
            self.autoScheduler.actionList.append(action)
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_addVisionAlignAction(self, button):
        self.autoScheduler.actionList.append(auto_actions.createVisionAlignAction(self.superDrive, self.vision))
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_pauseScheduler(self, button):
        self.autoScheduler.pause()

    @sea.queuedDashboardEvent
    def c_resumeScheduler(self, button):
        self.autoScheduler.unpause()

    @sea.queuedDashboardEvent
    def c_wheelsToZero(self, button):
        for wheel in self.superDrive.wheels:
            wheel._setSteering(0)

    @sea.queuedDashboardEvent
    def c_resetPosition(self, button):
        self.pathFollower.setPosition(
            self.app.selectedCoord.x, self.app.selectedCoord.y, self.app.selectedCoord.orientation)

    @sea.queuedDashboardEvent
    def c_slowVoltageGear(self, button):
        self.setGear(drivetrain.slowVoltageGear)

    @sea.queuedDashboardEvent
    def c_mediumVoltageGear(self, button):
        self.setGear(drivetrain.mediumVoltageGear)

    @sea.queuedDashboardEvent
    def c_fastVoltageGear(self, button):
        self.setGear(drivetrain.fastVoltageGear)

    @sea.queuedDashboardEvent
    def c_slowPositionGear(self, button):
        self.setGear(drivetrain.slowPositionGear)

    @sea.queuedDashboardEvent
    def c_mediumPositionGear(self, button):
        self.setGear(drivetrain.mediumPositionGear)

    @sea.queuedDashboardEvent
    def c_fastPositionGear(self, button):
        self.setGear(drivetrain.fastPositionGear)

    @sea.queuedDashboardEvent
    def c_disableWheel(self, button):
        self.superDrive.wheels[button.wheelNum - 1].angledWheel.driveMode = ctre.ControlMode.Disabled
        self.app.switchDeadWheelText(button)

    @sea.queuedDashboardEvent
    def c_toggleAutoScheduler(self, button):
        self.app.toggleAutoScheduler(button)
        self.toggleAutoScheduler()

    @sea.queuedDashboardEvent
    def c_clearAll(self, button):
        self.autoScheduler.clearActions()
        self.app.updateScheduler()
    
    @sea.queuedDashboardEvent
    def c_cancelRunningAction(self, button):
        self.autoScheduler.cancelRunningAction()

if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)