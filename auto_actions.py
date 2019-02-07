import math
import seamonsters as sea
from auto_scheduler import Action
import auto_vision

def createWaitAction(time):
    return Action("Wait " + str(time), lambda: sea.wait(int(time * 50)))

def createDriveToPointAction(pathFollower, x, y, angle, time):
    def generator():
        newAngle = sea.circleDistance(pathFollower.robotAngle, angle) + pathFollower.robotAngle
        yield from sea.ensureTrue(
            pathFollower.driveToPointGenerator(x, y, newAngle, time, math.radians(1)),
            10)
    return Action("Drive to (%f, %f, %f) for %f" % (x, y, math.degrees(angle), time),
        generator, coords=[(x, y)])

def createVisionAlignAction(drive, vision):
    return Action("Vision align", lambda: auto_vision.strafeAlign(drive, vision))
