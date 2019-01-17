import wpilib
import ctre

class grabber():

    def __init__(self):
        self.leftSpinner = ctre.WPI_TalonSRX(0)
        self.rightSpinner = ctre.WPI_TalonSRX(1)
        self.leftPivot = ctre.WPI_TalonSRX(2)
        self.rightPivot = ctre.WPI_TalonSRX(3)
        self.hatchGrabber = wpilib.Solenoid(0)

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