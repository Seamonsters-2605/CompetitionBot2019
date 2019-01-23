import math
import seamonsters as sea

# is A to B closer clockwise or counterclockwise?
def clockwise(a, b):
    dist = sea.circleDistance(a, b)
    if dist > 0:
        return dist < math.pi
    else:
        return dist < -math.pi

class DriveCoordinates:

    def __init__(self, name, x, y, orientation):
        self.name = name
        self.x = x
        self.y = y
        self.orientation = orientation
        self.angle = math.atan2(self.y, self.x)

    def __repr__(self):
        return self.name

rocket1 = DriveCoordinates("Rocket1", 6, 12, math.radians(-135))
rocket2 = DriveCoordinates("Rocket2", 7.5, 10.5, math.radians(-90))
rocket3 = DriveCoordinates("Rocket3", 9, 12, math.radians(-45))
humanstation1 = DriveCoordinates("human1", 27, 10.8, math.radians(180))

# in counterclockwise order
waypoints = [
    DriveCoordinates("Waypoint1", 15, 0, math.radians(0)),
    DriveCoordinates("Waypoint2", 15, 7.5, math.radians(0)),
    DriveCoordinates("Waypoint3", -15, 7.5, math.radians(0)),
    DriveCoordinates("Waypoint4", -15, 0, math.radians(0)),
    DriveCoordinates("Waypoint5", -15, -7.5, math.radians(0)),
    DriveCoordinates("Waypoint6", 15, -7.5, math.radians(0))]

def findWaypoints(targetCoord, robotX, robotY):
    robotAngle = math.atan2(robotY, robotX)
    
    nearestCWWaypoint = -1
    pointI = 0
    while True:
        point = waypoints[pointI]
        if clockwise(robotAngle, point.angle):
            nearestCWWaypoint = pointI
        else:
            if nearestCWWaypoint != -1:
                break
        pointI += 1
        pointI %= len(waypoints)

    moveClockwise = clockwise(robotAngle, targetCoord.angle)

    pointI = nearestCWWaypoint
    if not moveClockwise:
        # start at nearest counterclockwise waypoint
        pointI += 1
        pointI %= len(waypoints)

    path = []
    while True:
        waypoint = waypoints[pointI]
        clockwiseFromWaypoint = clockwise(waypoint.angle, targetCoord.angle)
        if clockwiseFromWaypoint == moveClockwise:
            path.append(waypoint)
        else:
            break
        if moveClockwise:
            pointI -= 1 # negative indices are fine
        else:
            pointI += 1
            pointI %= len(waypoints)

    path.append(targetCoord)
    return path
