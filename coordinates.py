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
        return "%s (%f, %f, %f deg)" \
            % (self.name, self.x, self.y, math.degrees(self.orientation))

    def inQuadrant(self, quadrant):
        """
        :param quadrant: 0 - 3, counterclockwise, 0 is positive x/y
        """
        newX = self.x
        newY = self.y
        newOrient = self.orientation
        if quadrant == 1 or quadrant == 2:
            newX = -newX
            newOrient = math.pi - newOrient
        if quadrant == 2 or quadrant == 3:
            newY = -newY
            newOrient = -newOrient
        return DriveCoordinates(self.name + " quad " + str(quadrant), newX, newY, newOrient)

rocket1 = DriveCoordinates("Rocket1", 6.2, 11.6, math.radians(-135))
rocket2 = DriveCoordinates("Rocket2", 7.9, 10.6, math.radians(-90))
rocket3 = DriveCoordinates("Rocket3", 9.6, 11.6, math.radians(-45))
humanstation = DriveCoordinates("Human", 27, 11.2, math.radians(180))
cargo1 = DriveCoordinates("Cargo1", 1.7, 2.2, math.radians(90))
cargo2 = DriveCoordinates("Cargo2", 3.5, 2.2, math.radians(90))
cargo3 = DriveCoordinates("Cargo3", 5.3, 2.2, math.radians(90))

quadrantTargetPoints = [rocket1, rocket2, rocket3, humanstation, cargo1, cargo2, cargo3]
targetPoints = []
for quadrant in range(0, 4):
    for point in quadrantTargetPoints:
        targetPoints.append(point.inQuadrant(quadrant))

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
