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
    yield from driveToPoint(pathFollower, coordinates.findStartingPoint(coord, pathFollower.robotX, \
            pathFollower.robotY, pathFollower.robotAngle),speed)#robot drives somewhere without an obstacle before calculating path
    pathFinder = path_follower.PathFinder("field.png")
    waypoints = pathFinder.navigate([int(coord.x), int(coord.y)], [int(pathFollower.robotX), int(pathFollower.robotY)])
    del waypoints[len(waypoints) - 1]
    del waypoints[0]
    while True:#loops through and deletes unnesacarry points
        changed = False
        for pt in range(len(waypoints) - 3):
            if not coordinates.testCollision(waypoints[pt][0], waypoints[pt][1], waypoints[pt + 2][0], waypoints[pt + 2][1]):
                del waypoints[pt + 1]
                changed = True
                print("del1")
        for pt in range(2, len(waypoints) - 1):
            if not coordinates.testCollision(waypoints[len(waypoints) - pt - 1][0], waypoints[len(waypoints) - pt - 1][1], waypoints[len(waypoints) - pt - 3][0], waypoints[len(waypoints) - pt - 3][1]):
                del waypoints[len(waypoints) - pt - 2]
                changed = True
                print("del2")
        if not changed:
            break
    for pt in waypoints:
        point = coordinates.DriveCoordinate("name", pt[0], pt[1], coord.orientation)
        yield from driveToPoint(pathFollower, point, speed)
    finalPoint = coordinates.DriveCoordinate("name", coord.x, coord.y, coord.orientation)
    yield from driveToPoint(pathFollower, finalPoint, speed)#makes robot go to exact final location at the end

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
