import wpilib
import ctre
import seamonsters as sea

class GrabberArm():

    #uncomment the stuff if air compressor isn't starting

    def __init__(self):
        self.leftSpinner = ctre.WPI_TalonSRX(20)
        self.rightSpinner = ctre.WPI_TalonSRX(21)
        self.leftPivot = ctre.WPI_TalonSRX(22)
        self.rightPivot = ctre.WPI_TalonSRX(23)
        self.hatchGrabber = wpilib.Solenoid(0)
        #self.compressor = wpilib.Compressor(0)
        self.slideMotor = ctre.WPI_TalonSRX(19)

    #takes in the ball at the speed "speed"
    def intake(self, speed):
        self.leftSpinner.set(speed)
        self.rightSpinner.set(-speed)

    #shoots out the ball at the speed "speed"
    def eject(self, speed):
        self.leftSpinner.set(-speed)
        self.rightSpinner.set(speed)

    #clamps the grabber arms at the speed "speed"
    def clamp(self, speed):
        self.leftPivot.set(speed)
        self.rightPivot.set(-speed)

    #releases the grabber arms at the speed "speed"
    def release(self, speed):
        self.leftPivot.set(-speed)
        self.rightPivot.set(speed)

    #pushes out the hatch grabber
    def push(self):
        self.hatchGrabber.set(True)

    #pulls in the hatch grabber
    def pull(self):
        self.hatchGrabber.set(False)

    #clamps the arms while running the intake wheels to grab the ball
    def grabBall(self, clampSpeed, intakeSpeed):
        self.clamp(clampSpeed)
        self.intake(intakeSpeed)

    #releases the arms and ejects the ball
    def releaseBall(self, releaseSpeed, ejectSpeed):
        self.eject(1)
        self.release(1)

    def stop(self):
        self.clamp(0)
        self.intake(0)

    #grabber slides up
    def slideUp(self, speed):
        self.slideMotor.set(speed)
    
    #grabber slides down
    def slideDown(self, speed):
        self.slideMotor.set(-speed)