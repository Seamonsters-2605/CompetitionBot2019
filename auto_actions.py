import math
import seamonsters as sea
from auto_scheduler import Action
import auto_vision

def driveToPoint(pathFollower, x, y, angle, speed):
    angle = sea.circleDistance(pathFollower.robotAngle, angle) + pathFollower.robotAngle
    dist = math.hypot(x - pathFollower.robotX, y - pathFollower.robotY)
    if dist < 0.1:
        time = 1
    else:
        time = dist / speed
    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(x, y, angle, time,
            math.radians(1), 1, math.radians(2)),
        25)

def createDriveToPointAction(pathFollower, x, y, angle, speed):
    return Action("Drive to (%f, %f, %f) at %f" % (x, y, math.degrees(angle), speed),
        lambda: driveToPoint(pathFollower, x, y, angle, speed),
        coords=[(x, y)])

def createVisionAlignAction(drive, vision):
    return Action("Vision align", lambda: auto_vision.strafeAlign(drive, vision))
