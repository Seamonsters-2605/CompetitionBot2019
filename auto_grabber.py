import math
import seamonsters as sea
import drivetrain

DRIVE_BACK_DIST = 1.5
DRIVE_BACK_TIME = 0.5

FORWARD = math.pi/2
BACKWARD = math.pi*3/2

def driveWait(pathFollower, time):
    for _ in range(time):
        pathFollower.updateRobotPosition()
        pathFollower.drive.drive(0, 0, 0)
        yield

def driveBackFromWall(pathFollower):
    drivetrain.autoPositionGear.applyGear(pathFollower.drive)
    angle = pathFollower.robotAngle
    targetX = pathFollower.robotX + math.sin(pathFollower.robotAngle) * DRIVE_BACK_DIST
    targetY = pathFollower.robotY - math.cos(pathFollower.robotAngle) * DRIVE_BACK_DIST
    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(targetX, targetY, angle, DRIVE_BACK_TIME,
                0.2, math.radians(2)),
        10)

def grabHatch(pathFollower, grabber):
    grabber.setGrabPiston(True)
    yield from driveWait(pathFollower, 15)

# with grabber in place, lift up and remove
def removeHatch(pathFollower, grabber):             # REMOVE HATCH
    grabber.elevatorLifted()                        # elevator lift up
    yield from driveWait(pathFollower, 25)          # wait for elevator TODO
    yield from driveBackFromWall(pathFollower)      # drive backward

def pickUpHatch(pathFollower, grabber):
    yield from grabHatch(pathFollower, grabber)
    yield from removeHatch(pathFollower, grabber)

def placeHatch(pathFollower, grabber):
    grabber.setGrabPiston(False)
    yield from driveWait(pathFollower, 15)

def depositHatch(pathFollower, grabber, pos):       # DEPOSIT HATCH
    grabber.elevatorHatchPosition(pos)              # move elevator to position
    yield from driveWait(pathFollower, 35*pos)      # wait for elevator TODO
    yield from placeHatch(pathFollower, grabber)
    grabber.elevatorHatchPosition(1)                # elevator down
    yield from driveWait(pathFollower, 25*pos)      # wait for elevator TODO
    yield from driveBackFromWall(pathFollower)      # drive backward

def depositCargo(pathFollower, grabber, pos):       # DEPOSIT CARGO
    grabber.elevatorCargoPosition(pos)              # move elevator to position
    yield from driveWait(pathFollower, 35*pos)      # wait for elevator TODO
    grabber.eject()                                 # eject cargo
    yield from driveWait(pathFollower, 25)          # wait for eject
    grabber.stopIntake()                            # stop intake
    grabber.elevatorCargoPosition(1)                # elevator down
    yield from driveWait(pathFollower, 25*pos)      # wait for elevator TODO
    yield from driveBackFromWall(pathFollower)      # drive backward
