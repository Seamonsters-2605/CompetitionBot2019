import wpilib
import ctre
import seamonsters as sea

DEFENSE_POSITION = 0
HATCH_POSITION = -300
OPEN_POSITION = -2841
CLOSED_POSITION = -3800

class GrabberArm():

    def __init__(self):
        self.leftSpinner = ctre.WPI_TalonSRX(20)
        self.rightSpinner = ctre.WPI_TalonSRX(21)
        self.leftPivot = ctre.WPI_TalonSRX(22)
        self.leftPivot.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        self.leftPivotOrigin = self.leftPivot.getSelectedSensorPosition(0)
        self.rightPivot = ctre.WPI_TalonSRX(23)
        self.rightPivot.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        self.rightPivotOrigin = self.rightPivot.getSelectedSensorPosition(0)
        self.rightPivot.setSensorPhase(True)
        self.hatchGrabberOut1 = wpilib.Solenoid(0)
        self.hatchGrabberIn1 = wpilib.Solenoid(1)
        self.hatchGrabberOut2 = wpilib.Solenoid(2)
        self.hatchGrabberIn2 = wpilib.Solenoid(3)
        self.compressor = wpilib.Compressor(0)
        self.slideMotor = ctre.WPI_TalonSRX(30)

    #takes in the ball at the speed "speed"
    def intake(self):
        self.leftSpinner.set(0.35)
        self.rightSpinner.set(-0.35)

    #shoots out the ball at the speed "speed"
    def eject(self):
        self.leftSpinner.set(-1)
        self.rightSpinner.set(1)

    def stopIntake(self):
        self.leftSpinner.set(0)
        self.rightSpinner.set(0)

    #clamps the grabber arms at the speed "speed"
    def clawClosed(self):
        self.leftPivot.set(ctre.ControlMode.Position, self.leftPivotOrigin + CLOSED_POSITION)
        self.rightPivot.set(ctre.ControlMode.Position, self.rightPivotOrigin - CLOSED_POSITION)

    #releases the grabber arms at the speed "speed"
    def clawOpen(self):
        self.leftPivot.set(ctre.ControlMode.Position, self.leftPivotOrigin + OPEN_POSITION)
        self.rightPivot.set(ctre.ControlMode.Position, self.rightPivotOrigin - OPEN_POSITION)

    def clawBack(self):
        self.leftPivot.set(ctre.ControlMode.Position, self.leftPivotOrigin + DEFENSE_POSITION)
        self.rightPivot.set(ctre.ControlMode.Position, self.rightPivotOrigin - DEFENSE_POSITION)

    def clawHatch(self):
        self.leftPivot.set(ctre.ControlMode.Position, self.leftPivotOrigin + HATCH_POSITION)
        self.rightPivot.set(ctre.ControlMode.Position, self.rightPivotOrigin - HATCH_POSITION)

    #clamps the arms while running the intake wheels to grab the ball
    def grabBall(self):
        self.clawClosed()
        self.intake()

    def setInnerPiston(self, value):
        self.hatchGrabberOut1.set(not value)
        self.hatchGrabberIn1.set(value)

    def setOuterPiston(self, value):
        self.hatchGrabberOut2.set(value)
        self.hatchGrabberIn2.set(not value)

    #grabber slides up
    def slide(self, speed):
        self.slideMotor.set(speed)

    def startCompressor(self):
        self.compressor.start()

    def stopCompressor(self):
        self.compressor.stop()
