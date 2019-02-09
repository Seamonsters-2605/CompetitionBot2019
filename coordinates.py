import math
import seamonsters as sea
import drivetrain

WALL_MARGIN = 19 / 12

# is A to B closer clockwise or counterclockwise?
def clockwise(a, b):
    return sea.circleDistance(a, b) < 0

class DriveCoordinate:

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
        return DriveCoordinate(self.name + " quad " + str(quadrant),
            newX, newY, newOrient)
    
    def moveAwayFromWall(self):
        return DriveCoordinate(self.name,
            self.x + math.sin(self.orientation) * WALL_MARGIN,
            self.y - math.cos(self.orientation) * WALL_MARGIN,
            self.orientation)

    def withOrientation(self, orientation):
        return DriveCoordinate(self.name, self.x, self.y, orientation)


rocket1 = DriveCoordinate("Rocket1", 6.2, 11.6, math.radians(-60)).moveAwayFromWall()
rocket2 = DriveCoordinate("Rocket2", 7.9, 10.6, math.radians(0)).moveAwayFromWall()
rocket3 = DriveCoordinate("Rocket3", 9.6, 11.6, math.radians(60)).moveAwayFromWall()
humanstation = DriveCoordinate("Human", 27, 11.2, math.radians(-90)).moveAwayFromWall()
cargo1 = DriveCoordinate("Cargo1", 1.7, 2.2, math.radians(180)).moveAwayFromWall()
cargo2 = DriveCoordinate("Cargo2", 3.5, 2.2, math.radians(180)).moveAwayFromWall()
cargo3 = DriveCoordinate("Cargo3", 5.3, 2.2, math.radians(180)).moveAwayFromWall()
cargo4 = DriveCoordinate("Cargo4", 8.4, 1.0, math.radians(90)).moveAwayFromWall()

quadrantTargetPoints = [rocket1, rocket2, rocket3, humanstation, cargo1, cargo2, cargo3, cargo4]
targetPoints = []
for quadrant in range(0, 4):
    for point in quadrantTargetPoints:
        targetPoints.append(point.inQuadrant(quadrant))

WAYPOINT_BOX_X = 13.5
WAYPOINT_BOX_Y = 6.5

# in counterclockwise order
waypoints = [
    DriveCoordinate("Waypoint1", WAYPOINT_BOX_X, WAYPOINT_BOX_Y, 0),
    DriveCoordinate("Waypoint2", -WAYPOINT_BOX_X, WAYPOINT_BOX_Y, 0),
    DriveCoordinate("Waypoint3", -WAYPOINT_BOX_X, -WAYPOINT_BOX_Y, 0),
    DriveCoordinate("Waypoint4", WAYPOINT_BOX_X, -WAYPOINT_BOX_Y, 0)]

def findWaypoints(targetCoord, robotX, robotY, robotAngle):
    robotCoord = DriveCoordinate("Robot", robotX, robotY, robotAngle)
    way1 = nearestBoxCoord(robotCoord)
    way2 = nearestBoxCoord(targetCoord)
    path = pathAroundBox(way1, way2)
    path.append(targetCoord)
    return path

def nearestBoxCoord(coord):
    x = coord.x
    y = coord.y
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
    nearest90DegreeAngle = coord.orientation + sea.circleDistance(coord.orientation, 0, math.pi / 2)
    return DriveCoordinate("Box point", x, y, nearest90DegreeAngle)


def pathAroundBox(way1, way2):
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
            path.append(waypoint.withOrientation(way1.orientation))
        else:
            break
        if moveClockwise:
            pointI -= 1 # negative indices are fine
        else:
            pointI += 1
            pointI %= len(waypoints)

    path.append(way2)
    return path

class Obstacle:

    def __init__(self, x1, y1, x2, y2):#1 = bottom left 2 = top right
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        #makes a square out of 4 line segments make a box representing an obstacle
        self.sides = [LineSegment(x1, y1, x1, y2), LineSegment(x1, y2, x2, y2), LineSegment(x2, y1, x2, y2), LineSegment(x1, y1, x2, y1)]

    def detectCollision(self, LineSegment):
        for side in self.sides:
            if LineSegment.collision(side):
                return True
        return False

class LineSegment:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        if x1 - x2 != 0:
            self.m = (y1 - y2) / (x1 - x2)
            self.b = self.m * x1 - y1
        else:
            self.m = None
            self.b = None

    def collision(self, LineSegment):
        if self.m == LineSegment.m:#if lines are parallel
            return False
        elif self.m == None and self.isBetween(LineSegment.x1, LineSegment.x2, self.x1) and self.isBetween(self.y1, self.y2, (LineSegment.y1 + LineSegment.m * (self.x1 - LineSegment.x1))):#if one line is straight up
            return True
        elif LineSegment.m == None and self.isBetween(self.x1, self.x2, LineSegment.x1) and self.isBetween(LineSegment.y1, LineSegment.y2, (self.y1 + self.m * (LineSegment.x1 - self.x1))):#if the other line is straight up, figured out by finding the change in x from an end on the non vertical line to the x value of the vertical one. this is then multiplied by the slope of the non vertical one and then added to the y value of the same end on the non vertical one as before, to get the y value on the non vertical line that has the same x as the vertical one. if that is between the y values on the vertical line, they intersect.
            return True
        elif self.isBetween(self.x1, self.x2, ((self.b - LineSegment.b) / (self.m - LineSegment.m))) and self.isBetween(self.y1, self.y2, ((self.b - LineSegment.b) / (self.m - LineSegment.m)) * self.m + self.b):
            return True
        return False


    def isBetween(self, end1, end2, find):
        bigger = end2
        smaller = end1
        if end1 > end2:
            bigger = end1
            smaller = end2
        if find < bigger and find > smaller:
            return True
        return False

