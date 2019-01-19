import math
import wpilib
import ctre
import navx
import seamonsters as sea
import drivetrain
import dashboard
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

        self.superDrive = drivetrain.initDrivetrain()
        
        self.ahrs = navx.AHRS.create_spi()

        self.pathFollower = sea.PathFollower(self.superDrive, self.ahrs)

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)

        self.autoScheduler = auto_scheduler.AutoScheduler()
        self.autoScheduler.updateCallback = self.updateScheduler

        self.drivegear = None

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
        self.setGear(drivetrain.mediumVelocityGear)
        self.resetPositions()
        yield from sea.parallel(self.autoScheduler.updateGenerator(),
            self.autoUpdate())

    def autoUpdate(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            if self.app is not None:
                self.app.doEvents()
            self.updateDashboardPositions()
            yield

    def teleop(self):
        self.setGear(drivetrain.mediumVoltageGear)

        self.resetPositions()
        if self.app is not None:
            self.app.clearEvents()

        while True:
            if self.app is not None:
                self.app.doEvents()
            x = self.joystick.getX()
            y = self.joystick.getY()
            mag = sea.deadZone(math.hypot(x * (1 - 0.5*y**2) ** 0.5,y * (1 - 0.5*x**2) ** 0.5))
            mag *= self.drivegear.moveScale
            direction = -self.joystick.getDirectionRadians() + math.pi/2
            turn = -sea.deadZone(self.joystick.getRawAxis(3))
            turn *= self.drivegear.turnScale # maximum radians per second

            if not self.joystick.getPOV() == -1:
                turn = self.circleDistance(math.radians(self.joystick.getPOV()), math.radians(self.ahrs.getAngle()))
                turn *= math.radians(60)
            
            self.superDrive.drive(mag, direction, turn)

            # encoder based position tracking
            self.pathFollower.updateRobotPosition()

            self.updateDashboardPositions()

            yield
    
    def updateDashboardPositions(self):
        if self.app != None:
            self.app.encoderPositionLbl.set_text('%.3f, %.3f, %.3f' %
                (self.pathFollower.robotX, self.pathFollower.robotY,
                math.degrees(self.pathFollower.robotAngle)))
            self.app.navxPositionLbl.set_text('%.3f, %.3f, %.3f' %
                (self.ahrs.getDisplacementX(), self.ahrs.getDisplacementY(),
                math.degrees(self.pathFollower._getAHRSAngle())))

    # dashboard callbacks

    def c_addWaitAction(self, button):
        waitTime = float(self.app.waitTimeInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createWaitAction(waitTime))
        self.updateScheduler()

    def c_addDriveToPointAction(self, button):
        pointX = float(self.app.pointXInput.get_value())
        pointY = float(self.app.pointYInput.get_value())
        pointAngle = math.radians(float(self.app.pointAngleInput.get_value()))
        moveTime = float(self.app.waitTimeInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createDriveToPointAction(self.pathFollower, pointX, pointY, pointAngle, moveTime))
        self.updateScheduler()

    def c_pauseScheduler(self, button):
        self.autoScheduler.paused = True

    def c_resumeScheduler(self, button):
        self.autoScheduler.paused = False

    def c_zeroSteering(self, button):
        for wheel in self.superDrive.wheels:
            wheel.zeroSteering()
    
    def c_zeroPosition(self, button):
        self.pathFollower.setPosition(0, 0, 0)
    
    def c_slowVoltageGear(self, button):
        self.setGear(drivetrain.slowVoltageGear)
    
    def c_mediumVoltageGear(self, button):
        self.setGear(drivetrain.mediumVoltageGear)
    
    def c_fastVoltageGear(self, button):
        self.setGear(drivetrain.fastVoltageGear)
    
    def c_slowVelocityGear(self, button):
        self.setGear(drivetrain.slowVelocityGear)
    
    def c_mediumVelocityGear(self, button):
        self.setGear(drivetrain.mediumVelocityGear)
    
    def c_fastVelocityGear(self, button):
        self.setGear(drivetrain.fastVelocityGear)


if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)
