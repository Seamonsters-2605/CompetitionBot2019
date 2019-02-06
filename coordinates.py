import math
import seamonsters as sea
import drivetrain

WALL_MARGIN = 19 / 12

# is A to B closer clockwise or counterclockwise?
def clockwise(a, b):
    return sea.circleDistance(a, b) < 0

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
            newOrient = -newOrient
        if quadrant == 2 or quadrant == 3:
            newY = -newY
            newOrient = math.pi - newOrient
        return DriveCoordinates(self.name + " quad " + str(quadrant),
            newX, newY, newOrient)
    
    def moveAwayFromWall(self):
        return DriveCoordinates(self.name,
            self.x + math.sin(self.orientation) * WALL_MARGIN,
            self.y - math.cos(self.orientation) * WALL_MARGIN,
            self.orientation)

rocket1 = DriveCoordinates("Rocket1", 6.2, 11.6, math.radians(-60)).moveAwayFromWall()
rocket2 = DriveCoordinates("Rocket2", 7.9, 10.6, math.radians(0)).moveAwayFromWall()
rocket3 = DriveCoordinates("Rocket3", 9.6, 11.6, math.radians(60)).moveAwayFromWall()
humanstation = DriveCoordinates("Human", 27, 11.2, math.radians(-90)).moveAwayFromWall()
cargo1 = DriveCoordinates("Cargo1", 1.7, 2.2, math.radians(180)).moveAwayFromWall()
cargo2 = DriveCoordinates("Cargo2", 3.5, 2.2, math.radians(180)).moveAwayFromWall()
cargo3 = DriveCoordinates("Cargo3", 5.3, 2.2, math.radians(180)).moveAwayFromWall()

quadrantTargetPoints = [rocket1, rocket2, rocket3, humanstation, cargo1, cargo2, cargo3]
targetPoints = []
for quadrant in range(0, 4):
    for point in quadrantTargetPoints:
        targetPoints.append(point.inQuadrant(quadrant))

WAYPOINT_BOX_X = 13.5
WAYPOINT_BOX_Y = 6.5

# in counterclockwise order
waypoints = [
    DriveCoordinates("Waypoint1", WAYPOINT_BOX_X, WAYPOINT_BOX_Y, math.radians(0)),
    DriveCoordinates("Waypoint2", -WAYPOINT_BOX_X, WAYPOINT_BOX_Y, math.radians(0)),
    DriveCoordinates("Waypoint3", -WAYPOINT_BOX_X, -WAYPOINT_BOX_Y, math.radians(0)),
    DriveCoordinates("Waypoint4", WAYPOINT_BOX_X, -WAYPOINT_BOX_Y, math.radians(0))]

def findWaypoints(targetCoord, robotX, robotY):
    way1 = nearestWaypointOnBox(robotX, robotY)
    way2 = nearestWaypointOnBox(targetCoord.x, targetCoord.y)
    path = pathBetweenWaypoints(way1, way2)
    path.append(targetCoord)
    return path

def nearestWaypointOnBox(x, y):
    insideX = False
    if x > WAYPOINT_BOX_X:
        x = WAYPOINT_BOX_X
    elif x < -WAYPOINT_BOX_X:
        x = -WAYPOINT_BOX_X
    else:
        insideX = True
    insideY = False
    if y > WAYPOINT_BOX_Y:
        y = WAYPOINT_BOX_Y
    elif y < -WAYPOINT_BOX_Y:
        y = -WAYPOINT_BOX_Y
    else:
        insideY = True
    if insideX and insideY:
        if x > 0:
            xClosest = WAYPOINT_BOX_X
        else:
            xClosest = -WAYPOINT_BOX_X
        if y > 0:
            yClosest = WAYPOINT_BOX_Y
        else:
            yClosest = - WAYPOINT_BOX_Y
        xDist = abs(x - xClosest)
        yDist = abs(y - yClosest)
        if xDist < yDist:
            x = xClosest
        else:
            y = yClosest
    return DriveCoordinates("Waypoint", x, y, 0)


def pathBetweenWaypoints(way1, way2):
    nearestCWWaypoint = -1
    pointI = 0
    while True:
        point = waypoints[pointI]
        if clockwise(way1.angle, point.angle):
            nearestCWWaypoint = pointI
        else:
            if nearestCWWaypoint != -1:
                break
        pointI += 1
        pointI %= len(waypoints)

    moveClockwise = clockwise(way1.angle, way2.angle)

    pointI = nearestCWWaypoint
    if not moveClockwise:
        # start at nearest counterclockwise waypoint
        pointI += 1
        pointI %= len(waypoints)

    path = []
    path.append(way1)
    while True:
        waypoint = waypoints[pointI]
        clockwiseFromWaypoint = clockwise(waypoint.angle, way2.angle)
        if clockwiseFromWaypoint == moveClockwise:
            path.append(waypoint)
        else:
            break
        if moveClockwise:
            pointI -= 1 # negative indices are fine
        else:
            pointI += 1
            pointI %= len(waypoints)

    path.append(way2)
    return path
