import wpilib
import ctre
import seamonsters as sea

DEFENSE_POSITION = 0
HATCH_POSITION = -891
OPEN_POSITION = -3104
CLOSED_POSITION = -3634
ELEVATOR_FLOOR = 3514
ELEVATOR_CARGO_POSITIONS = [-43508, -109364, -109364] # TODO level 3
ELEVATOR_HATCH_POSITIONS = [-21154, -89260, -149598]

class GrabberArm():

    def __init__(self):
        self.leftSpinner = ctre.WPI_TalonSRX(20)
        self.rightSpinner = ctre.WPI_TalonSRX(21)

        self.leftPivot = ctre.WPI_TalonSRX(22)
        self.setupPivotTalon(self.leftPivot)
        self.rightPivot = ctre.WPI_TalonSRX(23)
        self.setupPivotTalon(self.rightPivot)

        # TODO fix names
        self.solenoid0 = wpilib.Solenoid(0)
        self.solenoid1 = wpilib.Solenoid(1)
        self.solenoid2 = wpilib.Solenoid(2)
        self.solenoid3 = wpilib.Solenoid(3)
        self.compressor = wpilib.Compressor(0)

        self.slideMotor = ctre.WPI_TalonSRX(30)
        self.slideMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        self.slideMotor.setSensorPhase(False)
        self.slideMotor.config_kP(0, 0.3, 0)
        self.slideMotor.config_kI(0, 0, 0)
        self.slideMotor.config_kD(0, 3, 0)
        self.slideMotor.config_kF(0, 0, 0)
        self.slideValue = None

        self.resetAllSensors()

    def setupPivotTalon(self, talon):
        talon.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        talon.setSensorPhase(True)
        talon.config_kP(0, 1, 0)
        talon.config_kI(0, 0, 0)
        talon.config_kD(0, 3, 0)
        talon.config_kF(0, 0, 0)

    def resetAllSensors(self):
        self.leftPivotOrigin = self.leftPivot.getSelectedSensorPosition(0)
        self.rightPivotOrigin = self.rightPivot.getSelectedSensorPosition(0)
        self.slideOrigin = self.slideMotor.getSelectedSensorPosition(0)

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
        self.solenoid1.set(value)
        self.solenoid0.set(not value)

    def setOuterPiston(self, value):
        self.solenoid3.set(value)
        self.solenoid2.set(not value)

    #grabber slides up
    def elevatorSlide(self, speed):
        speed *= -1
        speed -= .05
        if speed != self.slideValue:
            self.slideMotor.set(speed)
            self.slideValue = speed

    def _setElevatorPosition(self, pos):
        pos += self.slideOrigin
        if pos != self.slideValue:
            self.slideMotor.set(ctre.ControlMode.Position, pos)
            self.slideValue = pos

    def elevatorFloor(self):
        self._setElevatorPosition(ELEVATOR_FLOOR)

    def elevatorCargoPosition(self, pos):
        self._setElevatorPosition(ELEVATOR_CARGO_POSITIONS[pos-1])

    def elevatorHatchPosition(self, pos):
        self._setElevatorPosition(ELEVATOR_HATCH_POSITIONS[pos-1])

    def startCompressor(self):
        self.compressor.start()

    def stopCompressor(self):
        self.compressor.stop()
