import math
import seamonsters as sea
from auto_scheduler import Action
import auto_vision
import auto_grabber
import coordinates
import drivetrain

VISION_APPROACH_MARGIN = 1 # how far past the wall to drive for vision align

def driveToPoint(pathFollower, vision, coord, speed):
    drivetrain.autoPositionGear.applyGear(pathFollower.drive)

    visionIntermediateCoord = coordinates.getVisionAlignIntermediatePoint(
        coord, pathFollower.robotX, pathFollower.robotY)
    if visionIntermediateCoord is not None:
        finalCoord = coord
        coord = visionIntermediateCoord

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
    
    # approach vision target
    if visionIntermediateCoord is not None:
        distanceToTarget = math.hypot(visionIntermediateCoord.x - coord.x,
                                      visionIntermediateCoord.y - coord.y)
        yield from auto_vision.driveIntoVisionTargetOrGiveUpAndDriveForward(
            pathFollower.drive, vision, pathFollower.drive, distanceToTarget + VISION_APPROACH_MARGIN)
        pathFollower.setPosition(finalCoord.x, finalCoord.y, None)

def createDriveToPointAction(pathFollower, vision, coord, speed):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, vision, coord, speed),
        coords=[(coord.x, coord.y)])

def navigateToPoint(pathFollower, vision, coord, speed):
    waypoints = coordinates.findWaypoints(coord,
        pathFollower.robotX, pathFollower.robotY, pathFollower.robotAngle)
    for pt in waypoints:
        yield from driveToPoint(pathFollower, vision, pt, speed)

def createNavigateToPointAction(pathFollower, vision, coord, speed):
    return Action("Navigate to " + coord.name,
        lambda: navigateToPoint(pathFollower, vision, coord, speed),
        coords=[(coord.x, coord.y)])

def createGenericAutoActions(pathFollower, grabber, vision):
    drive = pathFollower.drive
    return [
        Action("Pick up hatch", lambda: auto_grabber.pickUpHatch(drive, grabber, drive)),
        Action("Deposit hatch 1", lambda: auto_grabber.depositHatch(drive, grabber, 1, drive)),
        Action("Deposit hatch 2", lambda: auto_grabber.depositHatch(drive, grabber, 2, drive)),
        Action("Deposit hatch 3", lambda: auto_grabber.depositHatch(drive, grabber, 3, drive)),
        Action("Pick up cargo", lambda: auto_grabber.pickUpCargo(drive, grabber, drive)),
        Action("Deposit cargo 1", lambda: auto_grabber.depositCargo(drive, grabber, 1, drive)),
        Action("Deposit cargo 2", lambda: auto_grabber.depositCargo(drive, grabber, 2, drive)),
        Action("Deposit cargo 3", lambda: auto_grabber.depositCargo(drive, grabber, 3, drive))
    ]
