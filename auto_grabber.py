import math
import seamonsters as sea
import drivetrain

FORWARD = math.pi/2
BACKWARD = math.pi*3/2

def driveWait(drive, time):
    for _ in range(time):
        drive.drive(0, 0, 0)
        yield

def driveIntoWall(drive):
    drivetrain.autoVelocityGear.applyGear(drive)
    for _ in range(50):
        drive.drive(2, FORWARD, 0)
        yield
    yield from driveWait(drive, 25)

def driveBackFromWall(drive):
    drivetrain.autoPositionGear.applyGear(drive)
    for _ in range(25): # one foot?
        drive.drive(2, BACKWARD, 0)
        yield

def pickUpHatch(drive, grabber):                    # PICK UP HATCH
    grabber.elevatorHatchPosition(1)                     # elevator position 1
    grabber.setInnerPiston(True)                    # extend inner piston
    grabber.setOuterPiston(False)
    grabber.clawHatch()                             # claw in hatch position

    yield from driveIntoWall(drive)                 # drive into wall
    grabber.elevatorHatchPosition(2)                     # elevator lift up
    yield from driveWait(drive, 25)                 # wait for elevator
    yield from driveBackFromWall(drive)             # drive backward
    grabber.elevatorHatchPosition(1)                     # elevator down
    grabber.setInnerPiston(False)                   # retract inner piston
    drive.drive(0, 0, 0)
    yield                                           # END

def pickUpCargo(drive, grabber):                    # PICK UP CARGO
    grabber.elevatorCargoPosition(1)                     # elevator position 1
    grabber.setInnerPiston(False)
    grabber.setOuterPiston(False)
    grabber.clawOpen()                              # claw open
    yield from driveIntoWall(drive)                 # drive into wall
    grabber.clawClosed()                            # claw closed
    grabber.intake()                                # intake
    yield from driveWait(drive, 30)                 # wait for intake
    grabber.stopIntake()                            # stop intake
    yield from driveBackFromWall(drive)             # drive backward
    drive.drive(0, 0, 0)
    yield                                           # END

def depositHatch(drive, grabber, pos):              # DEPOSIT HATCH
    grabber.elevatorHatchPosition(pos)                   # move elevator to position
    yield from driveWait(drive, 25)                 # wait for elevator
    yield from driveIntoWall(drive)                 # drive into wall
    grabber.setOuterPiston(True)                    # extend outer pistons
    yield from driveWait(drive, 25)                 # wait for pistons
    yield from driveBackFromWall(drive)             # drive backward
    grabber.elevatorHatchPosition(1)                     # elevator down
    grabber.setOuterPiston(False)                   # retract outer pistons
    drive.drive(0, 0, 0)
    yield                                           # END

def depositCargo(drive, grabber, pos):              # DEPOSIT CARGO
    grabber.elevatorCargoPosition(pos)                   # move elevator to position
    yield from driveWait(drive, 25)                 # wait for elevator
    yield from driveIntoWall(drive)                 # drive into wall
    grabber.eject()                                 # eject cargo
    yield from driveWait(drive, 25)                 # wait for eject
    grabber.stopIntake()                            # stop intake
    yield from driveBackFromWall(drive)             # drive backward
    grabber.elevatorCargoPosition(1)                     # elevator down
    drive.drive(0, 0, 0)
    yield                                           # END
