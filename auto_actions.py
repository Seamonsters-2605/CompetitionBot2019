import math
import seamonsters as sea
from auto_scheduler import Action

def createWaitAction(time):
    return Action("Wait " + str(time), lambda: sea.wait(int(time * 50)))

def createDriveToPointAction(pathFollower, x, y, angle, time):
    return Action("Drive to (%f, %f, %f) for %f" % (x, y, math.degrees(angle), time),
        lambda: sea.ensureTrue(
            pathFollower.driveToPointGenerator(x, y, angle, time, math.radians(1)),
            10),
        coords=[(x, y)])
