import math
import ctre
import seamonsters as sea
from gear import DriveGear

# distance between center of wheels
WHEELBASE_WIDTH = 22.375 / 12 # feet
WHEELBASE_LENGTH = 22.375 / 12
# size of robot frame
ROBOT_WIDTH = 35.0 / 12
ROBOT_LENGTH = 35.0 / 12

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()
    _makeSwerveWheel(superDrive, 1, 0,  WHEELBASE_WIDTH/2,  WHEELBASE_LENGTH/2)
    _makeSwerveWheel(superDrive, 3, 2, -WHEELBASE_WIDTH/2,  WHEELBASE_LENGTH/2)
    _makeSwerveWheel(superDrive, 5, 4,  WHEELBASE_WIDTH/2, -WHEELBASE_LENGTH/2)
    _makeSwerveWheel(superDrive, 7, 6, -WHEELBASE_WIDTH/2, -WHEELBASE_LENGTH/2)
    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeSwerveWheel(superDrive, driveTalonNum, rotateTalonNum, xPos, yPos):
    driveTalon = ctre.WPI_TalonSRX(driveTalonNum)
    rotateTalon = ctre.WPI_TalonSRX(rotateTalonNum)
    driveTalon.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
    rotateTalon.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
    driveTalon.setSensorPhase(False)
    rotateTalon.setSensorPhase(False)

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
    p=0.07, i=0.0, d=12.0, f=0.0)
fastPositionGear = DriveGear("Fast Position", ctre.ControlMode.Position,
    moveScale=12, turnScale=math.radians(270),
    p=0.032, i=0.0, d=6.0, f=0.0)

autoPositionGear = DriveGear("Auto Position", ctre.ControlMode.Position,
    moveScale=12, turnScale=math.radians(270),
    p=0.07, i=0.0, d=12.0, f=0.0, realTime=False)
autoVelocityGear = DriveGear("Auto Velocity", ctre.ControlMode.Velocity,
    moveScale=12, turnScale=math.radians(270),
    p=0.07, i=0.0, d=12.0, f=0.0, realTime=False)
