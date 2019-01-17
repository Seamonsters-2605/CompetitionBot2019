import math
import ctre
import seamonsters as sea

ROBOT_WIDTH = 21.9950 / 12 # feet
ROBOT_LENGTH = 21.9950 / 12

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()
    _makeSwerveWheel(superDrive, 1, 0,  ROBOT_WIDTH/2,  ROBOT_LENGTH/2, True)
    _makeSwerveWheel(superDrive, 3, 2, -ROBOT_WIDTH/2,  ROBOT_LENGTH/2, True)
    _makeSwerveWheel(superDrive, 5, 4,  ROBOT_WIDTH/2, -ROBOT_LENGTH/2, True)
    _makeSwerveWheel(superDrive, 7, 6, -ROBOT_WIDTH/2, -ROBOT_LENGTH/2, True)
    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeSwerveWheel(superDrive, driveTalonNum, rotateTalonNum, xPos, yPos,
                     reverseSteerMotor):
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
                                    maxVoltageVelocity=16)

    # Steer motor:
    # 537.6 counts per revolution
    # 3 : 1 gear ratio
    # 537.6 * 3 = 1612.8 counts per wheel rotation
    swerveWheel = sea.SwerveWheel(angledWheel, rotateTalon, 1612.8, reverseSteerMotor)

    superDrive.addWheel(swerveWheel)

class DriveGear:

    def __init__(self, name, mode,
                 forwardScale=1.0, strafeScale=1.0, turnScale=1.0,
                 p=0.0, i=0.0, d=0.0, f=0.0):
        self.name = name
        self.mode = mode
        self.forwardScale = forwardScale
        self.strafeScale = strafeScale
        self.turnScale = turnScale
        self.p = p
        self.i = i
        self.d = d
        self.f = f

    def __repr__(self):
        return self.name


slowVoltageGear = DriveGear("Slow Voltage", ctre.ControlMode.PercentOutput,
    forwardScale=0.5, strafeScale=0.5, turnScale=math.radians(60),
    p=0.032, i=0.0, d=3.2, f=0.0) 
mediumVoltageGear = DriveGear("Medium Voltage", ctre.ControlMode.PercentOutput,
    forwardScale=3, strafeScale=3, turnScale=math.radians(90),
    p=0.032, i=0.0, d=3.2, f=0.0)
fastVoltageGear = DriveGear("Fast Voltage", ctre.ControlMode.PercentOutput,
    forwardScale=6, strafeScale=6, turnScale=math.radians(120),
    p=0.032, i=0.0, d=3.2, f=0.0)

slowVelocityGear = DriveGear("Slow Velocity", ctre.ControlMode.Velocity,
    forwardScale=0.5, strafeScale=0.5, turnScale=math.radians(60),
    p=0.032, i=0.0, d=3.2, f=0.0) 
mediumVelocityGear = DriveGear("Medium Velocity", ctre.ControlMode.Velocity,
    forwardScale=3, strafeScale=3, turnScale=math.radians(90),
    p=0.032, i=0.0, d=3.2, f=0.0)
fastVelocityGear = DriveGear("Fast Velocity", ctre.ControlMode.Velocity,
    forwardScale=6, strafeScale=6, turnScale=math.radians(120),
    p=0.032, i=0.0, d=3.2, f=0.0)
