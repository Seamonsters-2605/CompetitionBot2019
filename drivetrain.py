import math
import ctre
import seamonsters as sea

ROBOT_WIDTH = 21.9950 / 12 # feet
ROBOT_LENGTH = 21.9950 / 12

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()
    _makeSwerveWheel(superDrive, 1, 0,  ROBOT_WIDTH/2,  ROBOT_LENGTH/2, True)
    _makeSwerveWheel(superDrive, 3, 2, -ROBOT_WIDTH/2,  ROBOT_LENGTH/2, True)
    driveC, rotateC = _makeSwerveWheel(superDrive, 5, 4,  ROBOT_WIDTH/2, -ROBOT_LENGTH/2, True)
    rotateC.setSensorPhase(True)
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

    angledWheel = sea.AngledWheel(driveTalon, xPos, yPos, 0,
                                    encoderCountsPerFoot=31291.1352,
                                    maxVoltageVelocity=16)

    swerveWheel = sea.SwerveWheel(angledWheel, rotateTalon, 1612.8, reverseSteerMotor)

    superDrive.addWheel(swerveWheel)

    return driveTalon, rotateTalon 

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


slowgear = DriveGear("Slow", ctre.ControlMode.PercentOutput,
    forwardScale=0.5, strafeScale=0.5, turnScale=math.radians(60),
    p=0.032, i=0.0, d=3.2, f=0.0) 
mediumgear = DriveGear("Medium", ctre.ControlMode.PercentOutput,
    forwardScale=3, strafeScale=3, turnScale=math.radians(90),
    p=0.032, i=0.0, d=3.2, f=0.0)
fastgear = DriveGear("Fast", ctre.ControlMode.PercentOutput,
    forwardScale=6, strafeScale=6, turnScale=math.radians(120),
    p=0.032, i=0.0, d=3.2, f=0.0)
