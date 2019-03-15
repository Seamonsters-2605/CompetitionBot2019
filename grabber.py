import wpilib
import ctre
import seamonsters as sea

ELEVATOR_FLOOR = 0
ELEVATOR_LIFTED = 16390
ELEVATOR_CARGO_POSITIONS = [46631, 106474, 106474]
ELEVATOR_HATCH_POSITIONS = [0, 63328, 124587]

class GrabberArm():

    def __init__(self):
        self.topSpinner = ctre.WPI_TalonSRX(21)
        self.topSpinner.configFactoryDefault(0)
        self.bottomSpinner = ctre.WPI_TalonSRX(20)
        self.bottomSpinner.configFactoryDefault(0)

        # TODO fix names
        self.solenoid0 = wpilib.Solenoid(0)
        self.solenoid1 = wpilib.Solenoid(1)
        self.solenoid2 = wpilib.Solenoid(2)
        self.solenoid3 = wpilib.Solenoid(3)
        self.compressor = wpilib.Compressor(0)
        self.stopCompressor()

        self.armOut = False
        self.grabOut = False

        self.slideMotor = ctre.WPI_TalonSRX(30)
        self.slideMotor.configFactoryDefault(0)
        self.slideMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        self.slideMotor.setSensorPhase(False)
        self.slideMotor.config_kP(0, 0.3, 0)
        self.slideMotor.config_kI(0, 0, 0)
        self.slideMotor.config_kD(0, 3, 0)
        self.slideMotor.config_kF(0, 0, 0)
        self.slideMotor.configPeakOutputReverse(-0.75, 0)
        self.slideValue = None

        self.resetAllSensors()

    def resetAllSensors(self):
        self.slideOrigin = self.slideMotor.getSelectedSensorPosition(0)

    def disableAllMotors(self):
        self.elevatorSlide(0)
        self.stopIntake()

    #takes in the ball
    def intake(self):
        self.topSpinner.set(-0.35)
        self.bottomSpinner.set(-0.35)

    def cargoIdle(self):
        self.topSpinner.set(-0.15)
        self.bottomSpinner.set(-0.1)

    #shoots out the ball
    def eject(self):
        self.topSpinner.set(1)
        self.bottomSpinner.set(1)

    def stopIntake(self):
        self.topSpinner.set(0)
        self.bottomSpinner.set(0)

    def setArmPiston(self, value):
        self.solenoid1.set(value)
        self.solenoid0.set(not value)
        self.armOut = value

    def setGrabPiston(self, value):
        self.solenoid3.set(value)
        self.solenoid2.set(not value)
        self.grabOut = value

    #grabber slides up
    def elevatorSlide(self, speed):
        speed += .05
        if speed != self.slideValue:
            self.slideMotor.set(speed)
            self.slideValue = speed

    def _setElevatorPosition(self, pos):
        pos += self.slideOrigin
        if pos != self.slideValue:
            self.slideMotor.set(ctre.ControlMode.Position, pos)
            self.slideValue = pos

    def _getElevatorPosition(self):
        enc = self.slideMotor.getSelectedSensorPosition(0)
        return enc - self.slideOrigin

    def elevatorFloor(self):
        self._setElevatorPosition(ELEVATOR_FLOOR)

    def elevatorLifted(self):
        self._setElevatorPosition(ELEVATOR_LIFTED)

    def elevatorCargoPosition(self, pos):
        self._setElevatorPosition(ELEVATOR_CARGO_POSITIONS[pos-1])

    def elevatorHatchPosition(self, pos):
        self._setElevatorPosition(ELEVATOR_HATCH_POSITIONS[pos-1])

    def startCompressor(self):
        self.compressor.start()

    def stopCompressor(self):
        self.compressor.stop()
