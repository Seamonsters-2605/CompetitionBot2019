import wpilib
import ctre
import seamonsters as sea

DEFENSE_POSITION = 0
HATCH_POSITION = -300
OPEN_POSITION = -2841
CLOSED_POSITION = -3800
ELEVATOR_CARGO_POSITIONS = [0, 100, 200] # TODO TODO TODO!
ELEVATOR_HATCH_POSITIONS = [0, 100, 200]

class GrabberArm():

    def __init__(self):
        self.leftSpinner = ctre.WPI_TalonSRX(20)
        self.rightSpinner = ctre.WPI_TalonSRX(21)

        self.leftPivot = ctre.WPI_TalonSRX(22)
        self.leftPivot.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        self.leftPivot.setSensorPhase(False)
        self.leftPivotOrigin = self.leftPivot.getSelectedSensorPosition(0)
        self.rightPivot = ctre.WPI_TalonSRX(23)
        self.rightPivot.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        self.rightPivot.setSensorPhase(False)
        self.rightPivotOrigin = self.rightPivot.getSelectedSensorPosition(0)
        self.rightPivot.setSensorPhase(True)

        # TODO fix names
        self.hatchGrabberOut1 = wpilib.Solenoid(0)
        self.hatchGrabberIn1 = wpilib.Solenoid(1)
        self.hatchGrabberOut2 = wpilib.Solenoid(2)
        self.hatchGrabberIn2 = wpilib.Solenoid(3)

        self.compressor = wpilib.Compressor(0)

        self.slideMotor = ctre.WPI_TalonSRX(30)
        self.slideMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        self.slideMotor.setSensorPhase(False)
        self.slideOrigin = self.slideMotor.getSelectedSensorPosition(0)
        self.slideSpeed = None

    #takes in the ball
    def intake(self):
        self.leftSpinner.set(0.35)
        self.rightSpinner.set(-0.35)

    #shoots out the ball
    def eject(self):
        self.leftSpinner.set(-1)
        self.rightSpinner.set(1)

    def stopIntake(self):
        self.leftSpinner.set(0)
        self.rightSpinner.set(0)

    def _setClawPosition(self, position):
        self.leftPivot.set(ctre.ControlMode.Position, self.leftPivotOrigin + position)
        self.rightPivot.set(ctre.ControlMode.Position, self.rightPivotOrigin - position)

    def clawClosed(self):
        self._setClawPosition(CLOSED_POSITION)

    def clawOpen(self):
        self._setClawPosition(OPEN_POSITION)

    def clawBack(self):
        self._setClawPosition(DEFENSE_POSITION)

    def clawHatch(self):
        self._setClawPosition(HATCH_POSITION)

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
        if speed != self.slideSpeed:
            self.slideMotor.set(speed)
            self.slideSpeed = speed

    def elevatorCargoPosition(self, pos):
        self.slideMotor.set(ctre.ControlMode.Position,
            self.slideOrigin + ELEVATOR_CARGO_POSITIONS[pos-1])
        self.slideSpeed = None

    def elevatorHatchPosition(self, pos):
        self.slideMotor.set(ctre.ControlMode.Position,
            self.slideOrigin + ELEVATOR_HATCH_POSITIONS[pos-1])
        self.slideSpeed = None

    def startCompressor(self):
        self.compressor.start()

    def stopCompressor(self):
        self.compressor.stop()
