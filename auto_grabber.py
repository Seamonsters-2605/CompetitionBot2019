import math
import seamonsters as sea
import drivetrain

FORWARD = math.pi/2
BACKWARD = math.pi*3/2

def driveIntoWall(drive):
    drivetrain.autoVelocityGear.applyGear(drive)
    for _ in range(50):
        drive.drive(2, FORWARD, 0)
        yield
    for _ in range(25):
        drive.drive(0, 0, 0)
        yield

def driveBackFromWall(drive):
    drivetrain.autoPositionGear.applyGear(drive)
    for _ in range(25): # one foot?
        drive.drive(2, BACKWARD, 0)
        yield

def pickUpHatch(drive, grabber):
    grabber.elevatorPosition(1)
    grabber.setInnerPiston(True)                    # extend inner piston
    grabber.setOuterPiston(False)
    grabber.clawHatch()

    yield from driveIntoWall(drive)                 # drive into wall
    grabber.elevatorPosition(2)                     # lift up
    for _ in range(25):                             # wait
        drive.drive(0, 0, 0)
        yield
    yield from driveBackFromWall(drive)             # drive backward
    grabber.elevatorPosition(1)                     # elevator down
    grabber.setInnerPiston(False)                   # retract inner piston
    drive.drive(0, 0, 0)
    yield

def depositHatch(drive, grabber, pos):
    grabber.elevatorPosition(pos)                   # move elevator to position
    for _ in range(25):                             # wait
        drive.drive(0, 0, 0)
        yield
    yield from driveIntoWall(drive)                 # drive into wall
    grabber.setOuterPiston(True)                    # extend outer pistons
    for _ in range(25):                             # wait
        drive.drive(0, 0, 0)
        yield
    yield from driveBackFromWall(drive)             # drive backward
    grabber.elevatorPosition(1)                     # elevator down
    grabber.setOuterPiston(False)                   # retract outer pistons
    drive.drive(0, 0, 0)
    yield
