import math
import seamonsters as sea
from auto_scheduler import Action
import auto_vision
import auto_grabber
import coordinates
import drivetrain
import path_follower

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
    pathFinder = path_follower.PathFinder("field.png")
    waypoints = pathFinder.navigate([int(pathFollower.robotX), int(pathFollower.robotY)], [int(coord.x), int(coord.y)])
    print(waypoints)
    for pt in waypoints:
        point = coordinates.DriveCoordinate("name", pt[0], pt[1], math.radians(0))
        yield from driveToPoint(pathFollower, point, speed)

def createNavigateToPointAction(pathFollower, coord, speed):
    return Action("Navigate to " + coord.name,
        lambda: navigateToPoint(pathFollower, coord, speed),
        coords=[(coord.x, coord.y)])

def setRobotPosition(pathFollower, coord):
    pathFollower.setPosition(coord.x, coord.y, coord.orientation)
    yield

def createSetRobotPositionAction(pathFollower, coord):
    return Action("Set robot to " + coord.name,
        lambda: setRobotPosition(pathFollower, coord),
        coords=[(coord.x, coord.y)])

def createGenericAutoActions(pathFollower, grabber, vision):
    drive = pathFollower.drive
    return [
        Action("Vision align", lambda:
            auto_vision.driveIntoVisionTargetOrGiveUpAndDriveForward(drive, vision, drive, 2)),
        Action("Pick up hatch", lambda: auto_grabber.pickUpHatch(drive, grabber)),
        Action("Deposit hatch 1", lambda: auto_grabber.depositHatch(drive, grabber, 1)),
        Action("Deposit hatch 2", lambda: auto_grabber.depositHatch(drive, grabber, 2)),
        Action("Deposit hatch 3", lambda: auto_grabber.depositHatch(drive, grabber, 3)),
        Action("Pick up cargo", lambda: auto_grabber.pickUpCargo(drive, grabber)),
        Action("Deposit cargo 1", lambda: auto_grabber.depositCargo(drive, grabber, 1)),
        Action("Deposit cargo 2", lambda: auto_grabber.depositCargo(drive, grabber, 2)),
        Action("Deposit cargo 3", lambda: auto_grabber.depositCargo(drive, grabber, 3))
    ]
