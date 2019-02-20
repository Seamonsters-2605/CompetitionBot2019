import math
import seamonsters as sea
import drivetrain

FORWARD = math.pi/2
BACKWARD = math.pi*3/2

def driveWait(drive, time):
    for _ in range(time):
        drive.drive(0, 0, 0)
        yield

def driveBackFromWall(drive):
    drivetrain.autoPositionGear.applyGear(drive)
    for _ in range(25): # one foot?
        drive.drive(2, BACKWARD, 0)
        yield

def pickUpHatch(drive, grabber, superDrive):        # PICK UP HATCH
    grabber.elevatorLifted()                        # elevator lift up
    yield from driveWait(drive, 25)                 # wait for elevator TODO
    yield from driveBackFromWall(superDrive)        # drive backward
    grabber.elevatorHatchPosition(1)                # elevator down
    grabber.setInnerPiston(False)                   # retract inner piston
    drive.drive(0, 0, 0)
    yield                                           # END

def pickUpCargo(drive, grabber, superDrive):        # PICK UP CARGO
    grabber.clawClosed()                            # claw closed
    grabber.intake()                                # intake
    yield from driveWait(drive, 30)                 # wait for intake
    grabber.stopIntake()                            # stop intake
    yield from driveBackFromWall(superDrive)        # drive backward
    drive.drive(0, 0, 0)
    yield                                           # END

def depositHatch(drive, grabber, pos, superDrive):  # DEPOSIT HATCH
    grabber.elevatorHatchPosition(pos)              # move elevator to position
    yield from driveWait(drive, 50)                 # wait for elevator TODO
    grabber.setOuterPiston(True)                    # extend outer pistons
    yield from driveWait(drive, 25)                 # wait for pistons
    yield from driveBackFromWall(superDrive)        # drive backward
    grabber.elevatorHatchPosition(1)                # elevator down
    grabber.setOuterPiston(False)                   # retract outer pistons
    drive.drive(0, 0, 0)
    yield                                           # END

def depositCargo(drive, grabber, pos, superDrive):  # DEPOSIT CARGO
    grabber.elevatorCargoPosition(pos)              # move elevator to position
    yield from driveWait(drive, 50)                 # wait for elevator TODO
    grabber.eject()                                 # eject cargo
    yield from driveWait(drive, 25)                 # wait for eject
    grabber.stopIntake()                            # stop intake
    yield from driveBackFromWall(superDrive)        # drive backward
    grabber.elevatorCargoPosition(1)                # elevator down
    drive.drive(0, 0, 0)
    yield                                           # END
