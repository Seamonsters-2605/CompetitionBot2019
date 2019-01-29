import math
import ctre
import seamonsters as sea

ROBOT_WIDTH = 21.9950 / 12 # feet
ROBOT_LENGTH = 21.9950 / 12

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()
    _makeSwerveWheel(superDrive, 1, 0,  ROBOT_WIDTH/2,  ROBOT_LENGTH/2)
    _makeSwerveWheel(superDrive, 3, 2, -ROBOT_WIDTH/2,  ROBOT_LENGTH/2)
    _makeSwerveWheel(superDrive, 5, 4,  ROBOT_WIDTH/2, -ROBOT_LENGTH/2)
    _makeSwerveWheel(superDrive, 7, 6, -ROBOT_WIDTH/2, -ROBOT_LENGTH/2)
    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeSwerveWheel(superDrive, driveTalonNum, rotateTalonNum, xPos, yPos):
    driveTalon = ctre.WPI_TalonSRX(driveTalonNum)
    rotateTalon = ctre.WPI_TalonSRX(rotateTalonNum)
    driveTalon.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
    rotateTalon.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)

    driveTalon.setNeutralMode(ctre.NeutralMode.Coast)
    rotateTalon.setNeutralMode(ctre.NeutralMode.Brake)

    # rotate talon PIDs (drive talon is configured by DriveGear)
    rotateTalon.config_kP(0, 30.0, 0)
    rotateTalon.config_kI(0, 0.0, 0)
    rotateTalon.config_kD(0, 24.0, 0)

    # Drive motor:
    # 8192 counts per encoder revolution
    # 4 : 1 gear ratio
    # 8192 * 4 = 32768 counts per wheel rotation
    # Wheel diameter: 3.97 in.
    # Wheel circumference: 3.97 * pi / 12 = 1.03934 ft
    # 32768 / 1.03934 = 31527.59199 counts per foot
    angledWheel = sea.AngledWheel(driveTalon, xPos, yPos, 0,
                                  encoderCountsPerFoot=31527.59199,
                                  maxVoltageVelocity=16, reverse=True)

    # Steer motor:
    # 537.6 counts per revolution
    # 3 : 1 gear ratio
    # 537.6 * 3 = 1612.8 counts per wheel rotation
    swerveWheel = sea.SwerveWheel(angledWheel, rotateTalon, 1612.8, 0, -0.06883518, reverseSteerMotor=True)

    superDrive.addWheel(swerveWheel)
class DriveGear:

    def __init__(self, name, mode, moveScale, turnScale,
                 p=0.0, i=0.0, d=0.0, f=0.0):
        self.name = name
        self.mode = mode
        self.moveScale = moveScale
        self.turnScale = turnScale
        self.p = p
        self.i = i
        self.d = d
        self.f = f

    def __repr__(self):
        return self.name


slowVoltageGear = DriveGear("Slow Voltage", ctre.ControlMode.PercentOutput,
    moveScale=2, turnScale=math.radians(60)) 
mediumVoltageGear = DriveGear("Medium Voltage", ctre.ControlMode.PercentOutput,
    moveScale=6, turnScale=math.radians(120))
fastVoltageGear = DriveGear("Fast Voltage", ctre.ControlMode.PercentOutput,
    moveScale=15, turnScale=math.radians(180))

slowPositionGear = DriveGear("Slow Position", ctre.ControlMode.Position,
    moveScale=2, turnScale=math.radians(60),
    p=0.2, i=0.0, d=6.0, f=0.0)
mediumPositionGear = DriveGear("Medium Position", ctre.ControlMode.Position,
    moveScale=6, turnScale=math.radians(180),
    p=0.07, i=0.0, d=6.0, f=0.0)
fastPositionGear = DriveGear("Fast Position", ctre.ControlMode.Position,
    moveScale=15, turnScale=math.radians(360),
    p=0.032, i=0.0, d=6.0, f=0.0)
