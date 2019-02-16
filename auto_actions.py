import math
import seamonsters as sea
from auto_scheduler import Action
import auto_vision
import auto_grabber
import coordinates
import drivetrain

def driveToPoint(pathFollower, coord, speed):
    drivetrain.autoPositionGear.applyGear(pathFollower.drive)
    angle = sea.circleDistance(pathFollower.robotAngle, coord.orientation) + pathFollower.robotAngle
    dist = math.hypot(coord.x - pathFollower.robotX, coord.y - pathFollower.robotY)
    if dist < 0.1:
        time = 1
    else:
        time = dist / speed
    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(coord.x, coord.y, angle, time,
            math.radians(1), 1),
        25)

def createDriveToPointAction(pathFollower, coord, speed):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, coord, speed),
        coords=[(coord.x, coord.y)])

def navigateToPoint(pathFollower, coord, speed):
    if coordinates.testCollision(pathFollower.robotX, pathFollower.robotY, coord.x, coord.y):
        waypoints = coordinates.findWaypoints(coord,
            pathFollower.robotX, pathFollower.robotY, pathFollower.robotAngle)
        for pt in waypoints:
            yield from driveToPoint(pathFollower, pt, speed)
    else:
        yield from driveToPoint(pathFollower, coord, speed)

def createNavigateToPointAction(pathFollower, coord, speed):
    return Action("Navigate to " + coord.name,
        lambda: navigateToPoint(pathFollower, coord, speed),
        coords=[(coord.x, coord.y)])

def createVisionAlignAction(drive, vision):
    return Action("Vision align", lambda: sea.ensureTrue(auto_vision.strafeAlign(drive, vision), 50))

def createPickUpHatchAction(drive, grabber):
    return Action("Pick up hatch", lambda: auto_grabber.pickUpHatch(drive, grabber))

def createDepositHatchAction(drive, grabber, pos):
    return Action("Deposit hatch", lambda: auto_grabber.depositHatch(drive, grabber, pos))
