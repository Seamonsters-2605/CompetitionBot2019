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

        self.pathFollower = sea.PathFollower(self.superDrive)

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)

        self.autoScheduler = auto_scheduler.AutoScheduler()
        self.autoScheduler.updateCallback = self.updateScheduler

    def updateScheduler(self):
        if self.app is not None:
            self.app.updateScheduler()

    def setDriveMode(self, mode):
        print("Drive mode:", mode)
        for wheel in self.superDrive.wheels:
            wheel.angledWheel.driveMode = mode

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
        print("Running auto")
        yield from sea.parallel(self.autoScheduler.updateGenerator(),
            self.autoUpdate())

    def autoUpdate(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            if self.app is not None:
                self.app.doEvents()
            yield

    def teleop(self):
        self.setGear(drivetrain.mediumgear)

        self.resetPositions()
        if self.app is not None:
            self.app.clearEvents()

        while True:
            if self.app is not None:
                self.app.doEvents()

            Forward = sea.deadZone(self.joystick.getX())
            Strafe = sea.deadZone(self.joystick.getY())
            Strafe *= self.drivegear.strafeScale
            Forward *= self.drivegear.forwardScale
            
            mag = math.sqrt(Forward**2 + Strafe**2)
            
            direction = -self.joystick.getDirectionRadians() + math.pi/2
            turn = -sea.deadZone(self.joystick.getRawAxis(3))
            turn *= self.drivegear.turnScale # maximum radians per second

            if not self.joystick.getPOV() == -1:
                turn = self.circleDistance(math.radians(self.joystick.getPOV()), math.radians(self.ahrs.getAngle()))
                turn *= math.radians(60)
            
            self.superDrive.drive(mag, direction, turn)

            # encoder based position tracking
            self.pathFollower.updateRobotPosition()

            if self.app != None:
                self.app.encoderPositionLbl.set_text('%.3f, %.3f, %.3f' %
                    (self.pathFollower.robotX, self.pathFollower.robotY,
                    math.degrees(self.pathFollower.robotAngle)))
                self.app.navxPositionLbl.set_text('%.3f, %.3f, %.3f' %
                    (self.ahrs.getDisplacementX(), self.ahrs.getDisplacementY(), self.ahrs.getAngle()))

            yield
    
    # dashboard callbacks

    def c_addWaitAction(self, button):
        waitTime = float(self.app.waitTimeInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createWaitAction(waitTime))
        self.updateScheduler()

    def c_pauseScheduler(self, button):
        self.autoScheduler.paused = True

    def c_resumeScheduler(self, button):
        self.autoScheduler.paused = False

    def c_zeroSteering(self, button):
        for wheel in self.superDrive.wheels:
            wheel.zeroSteering()
    
    def slow(self, button):
        self.setGear(drivetrain.slowgear)
    
    def medium(self, button):
        self.setGear(drivetrain.mediumgear)
    
    def fast(self, button):
        self.setGear(drivetrain.fastgear)


if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)
