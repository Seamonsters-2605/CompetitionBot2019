import wpilib
import ctre
import seamonsters as sea

DEFENSE_POSITION = 0
HATCH_POSITION = -891
OPEN_POSITION = -3219
CLOSED_POSITION = -3700
ELEVATOR_FLOOR = -3514
ELEVATOR_LIFTED = 36806
ELEVATOR_CARGO_POSITIONS = [40833, 105547, 150471]
ELEVATOR_HATCH_POSITIONS = [21154, 81352, 146561]

class GrabberArm():

    def __init__(self):
        self.leftSpinner = ctre.WPI_TalonSRX(20)
        self.rightSpinner = ctre.WPI_TalonSRX(21)

        self.leftPivot = ctre.WPI_TalonSRX(22)
        self.setupPivotTalon(self.leftPivot)
        self.rightPivot = ctre.WPI_TalonSRX(23)
        self.setupPivotTalon(self.rightPivot)

        self.clawState = None

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
        talon.setSensorPhase(False)
        talon.config_kP(0, 2, 0)
        talon.config_kI(0, 0, 0)
        talon.config_kD(0, 12, 0)
        talon.config_kF(0, 0, 0)
        talon.configClosedLoopPeakOutput(0, 0.5, 0)

    def resetAllSensors(self):
        self.leftPivotOrigin = self.leftPivot.getSelectedSensorPosition(0)
        self.rightPivotOrigin = self.rightPivot.getSelectedSensorPosition(0)
        self.slideOrigin = self.slideMotor.getSelectedSensorPosition(0)

    def disableAllMotors(self):
        self.leftPivot.disable()
        self.rightPivot.disable()
        self.elevatorSlide(0)
        self.clawState = None

    #takes in the ball
    def intake(self):
        self.leftSpinner.set(-0.35)
        self.rightSpinner.set(0.35)

    #shoots out the ball
    def eject(self):
        self.leftSpinner.set(1)
        self.rightSpinner.set(-1)

    def stopIntake(self):
        self.leftSpinner.set(0)
        self.rightSpinner.set(0)

    def _setClawPosition(self, position):
        print("set claw", position)
        return
        self.leftPivot.set(ctre.ControlMode.Position, self.leftPivotOrigin + position)
        self.rightPivot.set(ctre.ControlMode.Position, self.rightPivotOrigin - position)

    def clawClosed(self):
        if self.clawState == "closed":
            return
        if not self.safeForArmsToClose():
            return
        self.clawState = "closed"
        self._setClawPosition(CLOSED_POSITION)

    def clawOpen(self):
        if self.clawState == "open":
            return
        if not self.safeForArmsToClose():
            return
        self.clawState = "open"
        self._setClawPosition(OPEN_POSITION)

    def clawBack(self):
        if self.clawState == "back":
            return
        if not self.safeForArmsToGoBack():
            return
        self.clawState = "back"
        self._setClawPosition(DEFENSE_POSITION)

    def clawHatch(self):
        if self.clawState == "hatch":
            return
        self.clawState = "hatch"
        self._setClawPosition(HATCH_POSITION)

    #clamps the arms while running the intake wheels to grab the ball
    def grabBall(self):
        self.clawClosed()
        self.intake()

    def setInnerPiston(self, value):
        self.solenoid1.set(not value)
        self.solenoid0.set(value)

    def setOuterPiston(self, value):
        self.solenoid3.set(not value)
        self.solenoid2.set(value)

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

    def elevatorToZero(self):
        self._setElevatorPosition(0)

    def elevatorFloor(self):
        self._setElevatorPosition(ELEVATOR_FLOOR)

    def elevatorLifted(self):
        self._setElevatorPosition(ELEVATOR_LIFTED)

    def elevatorCargoPosition(self, pos):
        self._setElevatorPosition(ELEVATOR_CARGO_POSITIONS[pos-1])

    def elevatorHatchPosition(self, pos):
        self._setElevatorPosition(ELEVATOR_HATCH_POSITIONS[pos-1])

    def safeForArmsToGoBack(self):
        return self._getElevatorPosition() < ELEVATOR_HATCH_POSITIONS[0]

    def safeForArmsToClose(self):
        return self._getElevatorPosition() > 0

    def startCompressor(self):
        self.compressor.start()

    def stopCompressor(self):
        self.compressor.stop()
