import math
import wpilib
import ctre
import navx
import seamonsters as sea
import drivetrain
import dashboard
import buttons
import auto_scheduler
import auto_actions

class CompetitionBot2019(sea.GeneratorBot):

    def circleDistance(self, a, b):
        diff = a - b
        while diff > math.pi:
            diff -= math.pi * 2
        while diff < -math.pi:
            diff += math.pi * 2
        return diff

    def robotInit(self):
        self.joystick = wpilib.Joystick(0)

        self.pdp = wpilib.PowerDistributionPanel(50)

        self.superDrive = drivetrain.initDrivetrain()
        
        self.ahrs = navx.AHRS.create_spi()

        self.pathFollower = sea.PathFollower(self.superDrive, self.ahrs)

        self.headless_mode = False

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)

        self.autoScheduler = auto_scheduler.AutoScheduler()
        self.autoScheduler.updateCallback = self.updateScheduler

        self.timingMonitor = sea.TimingMonitor()

        self.drivegear = None

        self.button = buttons.Buttons(self.joystick)
        self.button.addPreset(3,buttons.Buttons.SINGLE_CLICK, self.switchHeadless, [])

        self.testDIO = wpilib.DigitalInput(0)

    def test(self):
        motor = self.superDrive.wheels[0].angledWheel.motor
        motor.set(ctre.ControlMode.PercentOutput, 1)
        while self.testDIO.get():
            yield
        while not self.testDIO.get():
            yield
        motor.set(ctre.ControlMode.PercentOutput, 0)

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
    
    def autonomous(self):
        self.setGear(drivetrain.mediumPositionGear)
        self.resetPositions()
        self.pathFollower.setPosition(0, 0, 0)
        yield from sea.parallel(self.autoScheduler.updateGenerator(),
            self.autoUpdate(), self.timingMonitor.updateGenerator())

    def autoUpdate(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            if self.app is not None:
                self.app.doEvents()
            self.updateDashboardLabels()
            yield

    def teleop(self):
        self.setGear(drivetrain.mediumPositionGear)
        self.resetPositions()
        self.pathFollower.setPosition(0, 0, 0)
        yield from sea.parallel(self.teleopUpdate(),
            self.timingMonitor.updateGenerator())

    def teleopUpdate(self):
        if self.app is not None:
            self.app.clearEvents()

        while True:
            if self.app is not None:
                self.app.doEvents()

            self.pathFollower.updateRobotPosition()

            x = self.joystick.getX()
            y = self.joystick.getY()
            mag = sea.deadZone(math.hypot(x * (1 - 0.5*y**2) ** 0.5,y * (1 - 0.5*x**2) ** 0.5))
            mag *= self.drivegear.moveScale

            direction = -self.joystick.getDirectionRadians() + math.pi/2

            if self.headless_mode:
                direction -= self.pathFollower.robotAngle
            
            turn = -sea.deadZone(self.joystick.getRawAxis(3))
            turn *= self.drivegear.turnScale # maximum radians per second

            if not self.joystick.getPOV() == -1:
                aDiff = self.circleDistance(-math.radians(self.joystick.getPOV()), self.pathFollower.robotAngle)
                turn = aDiff / 0.1 # seconds
                targetAVel = drivetrain.fastPositionGear.turnScale
                if turn > targetAVel:
                    turn = targetAVel
                elif turn < -targetAVel:
                    turn = -targetAVel

            self.superDrive.drive(mag, direction, turn)

            self.updateDashboardLabels()

            self.button.update()

            yield

    def updateDashboardLabels(self):
        if self.app != None:
            self.app.updateRobotPosition(
                self.pathFollower.robotX, self.pathFollower.robotY,
                self.pathFollower.robotAngle)
            self.app.realTimeRatioLbl.set_text(
                '%.3f' % (self.timingMonitor.realTimeRatio,))
            self.app.currentLbl.set_text(str(self.pdp.getTotalCurrent()))

    # button functions

    def switchHeadless(self):
        if self.headless_mode == False:
            self.headless_mode = True
            print("Headless Mode On")
        else:
            self.headless_mode = False
            print("Headless Mode Off")

    # dashboard callbacks

    @sea.queuedDashboardEvent
    def c_addWaitAction(self, button):
        waitTime = float(self.app.waitTimeInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createWaitAction(waitTime))
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_addDriveToPointAction(self, button):
        pointX = float(self.app.pointXInput.get_value())
        pointY = float(self.app.pointYInput.get_value())
        pointAngle = math.radians(float(self.app.pointAngleInput.get_value()))
        moveTime = float(self.app.waitTimeInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createDriveToPointAction(self.pathFollower, pointX, pointY, pointAngle, moveTime))
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_pauseScheduler(self, button):
        self.autoScheduler.paused = True

    @sea.queuedDashboardEvent
    def c_resumeScheduler(self, button):
        self.autoScheduler.paused = False

    @sea.queuedDashboardEvent
    def c_wheelsToZero(self, button):
        for wheel in self.superDrive.wheels:
            wheel._setSteering(0)

    @sea.queuedDashboardEvent
    def c_zeroPosition(self, button):
        self.pathFollower.setPosition(0, 0, 0)

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


if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)
