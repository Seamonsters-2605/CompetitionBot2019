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
            0.2, math.radians(2)),
        25)
    
    # approach vision target
    if visionIntermediateCoord is not None:
        distanceToTarget = math.hypot(coord.x - finalCoord.x, coord.y - finalCoord.y)
        yield from auto_vision.driveIntoVisionTargetOrGiveUpAndDriveForward(
            pathFollower.drive, vision, pathFollower.drive, distanceToTarget + VISION_APPROACH_MARGIN)
        pathFollower.setPosition(finalCoord.x, finalCoord.y, None)

def createDriveToPointAction(pathFollower, vision, coord, speed, key):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, vision, coord, speed), key,
        coords=[(coord.x, coord.y)])

def rotateInPlace(pathFollower, coord):
    coord = coordinates.DriveCoordinate("Rotated",
        pathFollower.robotX, pathFollower.robotY, coord.orientation)
    yield from driveToPoint(pathFollower, None, coord, 5)

def createRotateInPlaceAction(pathFollower, coord, key):
    return Action("Rotate to " + str(round(math.degrees(coord.orientation))),
        lambda: rotateInPlace(pathFollower, coord), key)

def navigateToPoint(pathFollower, vision, coord, speed):
    waypoints = coordinates.findWaypoints(coord,
        pathFollower.robotX, pathFollower.robotY, pathFollower.robotAngle)
    for pt in waypoints:
        yield from driveToPoint(pathFollower, vision, pt, speed)

def createNavigateToPointAction(pathFollower, vision, coord, speed, key):
    return Action("Navigate to " + coord.name,
        lambda: navigateToPoint(pathFollower, vision, coord, speed), key,
        coords=[(coord.x, coord.y)])

def createPickUpHatchAction(pathFollower, grabber, key):
    return Action("Pick up hatch",
        lambda: auto_grabber.pickUpHatch(pathFollower, grabber), key)

def endAuto(robot):
    yield
    robot.manualMode()

def createEndAction(robot, key):
    return Action("--END--", lambda: endAuto(robot), key)

def createGenericAutoActions(robot, pathFollower, grabber):
    return [
        createPickUpHatchAction(pathFollower, grabber, 0),
        Action("Deposit hatch 1", lambda: auto_grabber.depositHatch(pathFollower, grabber, 1), 1),
        Action("Deposit hatch 2", lambda: auto_grabber.depositHatch(pathFollower, grabber, 2), 2),
        Action("Deposit hatch 3", lambda: auto_grabber.depositHatch(pathFollower, grabber, 3), 3),
        Action("Deposit cargo 1", lambda: auto_grabber.depositCargo(pathFollower, grabber, 1), 4),
        Action("Deposit cargo 2", lambda: auto_grabber.depositCargo(pathFollower, grabber, 2), 5),
        Action("Deposit cargo 3", lambda: auto_grabber.depositCargo(pathFollower, grabber, 3), 6),
        createEndAction(robot, 7)

    ]
