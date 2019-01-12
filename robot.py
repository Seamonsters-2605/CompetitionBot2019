import math
import wpilib
import ctre
import navx
import seamonsters as sea
import drivetrain
import dashboard

class CompetitionBot2019(sea.GeneratorBot):

    def robotInit(self):
        self.joystick = wpilib.Joystick(0)

        self.superDrive = drivetrain.initDrivetrain()
        self.setDriveMode(ctre.ControlMode.PercentOutput)

        # for encoder-based position tracking
        self.robotOrigin = None
        self.robotX = 0
        self.robotY = 0
        self.robotAngle = 0
        
        self.ahrs = navx.AHRS.create_spi()

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)
        self.drivegear = None

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
        #print("Switch gear", gear)
        for wheel in self.superDrive.wheels:
            pidf = wheel.angledWheel.motor
            pidf.config_kP(0, self.drivegear.p, 0)
            pidf.config_kI(0, self.drivegear.i, 0)
            pidf.config_kD(0, self.drivegear.d, 0)
            pidf.config_kF(0, self.drivegear.F, 0)
        self.setDriveMode(gear.mode)
    
    def autonomous(self):
        self.resetPositions()
        self.setDriveMode(ctre.ControlMode.Position)

    def teleop(self):
        self.setGear(drivetrain.DriveGear(ctre.ControlMode.Velocity))

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

            self.superDrive.drive(mag, direction, turn)

            # encoder based position tracking
            moveMag, moveDir, moveTurn, self.robotOrigin = \
                self.superDrive.getRobotPositionOffset(self.robotOrigin)
            self.robotX += moveMag * math.cos(moveDir + self.robotAngle)
            self.robotY += moveMag * math.sin(moveDir + self.robotAngle)
            self.robotAngle += moveTurn

            if self.app != None:
                self.app.encoderPositionLbl.set_text('%.3f, %.3f, %.3f' %
                    (self.robotX, self.robotY, math.degrees(self.robotAngle)))
                self.app.navxPositionLbl.set_text('%.3f, %.3f, %.3f' %
                    (self.ahrs.getDisplacementX(), self.ahrs.getDisplacementY(), self.ahrs.getAngle()))

            yield
    
    # dashboard callbacks

    def c_zeroSteering(self, button):
        for wheel in self.superDrive.wheels:
            wheel.zeroSteering()
    
    def c_percentOutputMode(self, button):
        self.setDriveMode(ctre.ControlMode.PercentOutput)
    
    def c_velocityMode(self, button):
        self.setDriveMode(ctre.ControlMode.Velocity)
    
    def c_positionMode(self, button):
        self.setDriveMode(ctre.ControlMode.Position)


if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)
