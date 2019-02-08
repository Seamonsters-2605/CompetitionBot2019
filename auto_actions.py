import math
import seamonsters as sea
from auto_scheduler import Action
import auto_vision

def driveToPoint(pathFollower, coord, speed):
    angle = sea.circleDistance(pathFollower.robotAngle, coord.orientation) + pathFollower.robotAngle
    dist = math.hypot(coord.x - pathFollower.robotX, coord.y - pathFollower.robotY)
    if dist < 0.1:
        time = 1
    else:
        time = dist / speed
    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(coord.x, coord.y, angle, time,
            math.radians(1), 1, math.radians(2)),
        25)

def createDriveToPointAction(pathFollower, coord, speed):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, coord, speed),
        coords=[(coord.x, coord.y)])

def createVisionAlignAction(drive, vision):
    return Action("Vision align", lambda: auto_vision.strafeAlign(drive, vision))
