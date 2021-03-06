import math
import seamonsters as sea
import drivetrain

VISION_DISTANCE = 3 # feet

# is A to B closer clockwise or counterclockwise?
def clockwise(a, b):
    return sea.circleDistance(a, b) < 0

class DriveCoordinate:

    def __init__(self, name, x, y, orientation, visionTarget=False):
        self.name = name
        self.x = x
        self.y = y
        self.orientation = orientation
        self.angle = math.atan2(self.y, self.x)
        self.visionTarget = visionTarget

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
        return DriveCoordinate(self.name + " Q" + str(quadrant),
            newX, newY, newOrient, self.visionTarget)

    def moveForward(self, amount):
        return DriveCoordinate(self.name,
            self.x - math.sin(self.orientation) * amount,
            self.y + math.cos(self.orientation) * amount,
            self.orientation, self.visionTarget)
    
    def moveAwayFromWall(self):
        return self.moveForward(-drivetrain.ROBOT_LENGTH / 2)

    def moveTowardsWall(self):
        return self.moveForward(drivetrain.ROBOT_LENGTH / 2)

    def withOrientation(self, orientation):
        return DriveCoordinate(self.name, self.x, self.y, orientation, self.visionTarget)


rocket1 = DriveCoordinate("Rocket1", 6.7, 11.9, math.radians(-60), True).moveAwayFromWall() # from image
rocket2 = DriveCoordinate("Rocket2", 8.0, 134.56 / 12, math.radians(0), True).moveAwayFromWall() # from diagram
rocket3 = DriveCoordinate("Rocket3", 9.3, 11.9, math.radians(60), True).moveAwayFromWall() # from image
humanstation = DriveCoordinate("Human", 27, 11.3, math.radians(-90), True).moveAwayFromWall() # from image
cargo1 = DriveCoordinate("Ship1", 20.85 / 12, 27.75 / 12, math.radians(180), True).moveAwayFromWall() # x diagram, y manual
cargo2 = DriveCoordinate("Ship2", 42.6 / 12, 27.75 / 12, math.radians(180), True).moveAwayFromWall()
cargo3 = DriveCoordinate("Ship3", 64.35 / 12, 27.75 / 12, math.radians(180), True).moveAwayFromWall()
cargo4 = DriveCoordinate("Ship4", 8.7, 10.875 / 12, math.radians(90), True).moveAwayFromWall() # x image, y diagram

startLevel1 = DriveCoordinate("Hab side L1", 277.0 / 12, 3.6, math.radians(90)).moveTowardsWall() # x diagram, y image
startLevel2 = DriveCoordinate("Hab side L2", 27.0, 3.6, math.radians(-90)).moveAwayFromWall() # from image
startCenter = DriveCoordinate("Hab center L1", 277.0 / 12, 0, math.radians(90)).moveTowardsWall() # from diagram

offHabCenter = DriveCoordinate("Off Hab center", 19.1, 0, math.radians(90)).moveTowardsWall()
offHabSide = DriveCoordinate("Off Hab side", 19.1, 3.6, math.radians(-90)).moveAwayFromWall()

quadrantTargetPoints = [rocket1, rocket2, rocket3, humanstation,
    cargo1, cargo2, cargo3, cargo4, startLevel1, startLevel2, startCenter,
    offHabCenter, offHabSide]
targetPoints = []
for quadrant in range(0, 4):
    for point in quadrantTargetPoints:
        targetPoints.append(point.inQuadrant(quadrant))

def getVisionAlignIntermediatePoint(targetCoord, robotX, robotY):
    if not targetCoord.visionTarget:
        return None
    perpendicularDist = -(robotX-targetCoord.x) * math.sin(targetCoord.orientation) \
                       + (robotY-targetCoord.y) * math.cos(targetCoord.orientation)
    if perpendicularDist > 0: # in front of target
        perpendicularDist = -VISION_DISTANCE
    if perpendicularDist < -VISION_DISTANCE:
        perpendicularDist = -VISION_DISTANCE
    intermediate = targetCoord.moveForward(perpendicularDist)
    intermediate.visionTarget = False
    return intermediate


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

# will take in the actual coords of the corners of the obstacles and then
# account for the size of the robot for collision detection
class Obstacle:

    # 1 = bottom left 2 = top right
    def __init__(self, x1, y1, x2, y2):
        # 1/2 the longest length on the robot which will be added to all the
        # obstacles so the robot won't crash
        self.robotSize = drivetrain.ROBOT_LENGTH/2
        if drivetrain.ROBOT_WIDTH/2 > self.robotSize:
            self.robotSize = drivetrain.ROBOT_WIDTH/2
        elif math.sqrt(((drivetrain.ROBOT_LENGTH ** 2) + (drivetrain.ROBOT_WIDTH ** 2)))/2 > self.robotSize:
            self.robotSize = math.sqrt(drivetrain.ROBOT_LENGTH ** 2 + drivetrain.ROBOT_WIDTH ** 2)/2
        self.x1 = self.accountForRobotSize(x1, x2)[0]
        self.y1 = self.accountForRobotSize(y1, y2)[0]
        self.x2 = self.accountForRobotSize(x1, x2)[1]
        self.y2 = self.accountForRobotSize(y1, y2)[1]
        #makes a square out of 4 line segments make a box representing an obstacle
        self.sides = [LineSegment(x1, y1, x1, y2), LineSegment(x1, y2, x2, y2),
                      LineSegment(x2, y1, x2, y2), LineSegment(x1, y1, x2, y1)]

    # if collide -> return true, else -> return false
    def detectCollision(self, LineSegment):
        for side in self.sides:
            if LineSegment.collision(side):
                return True
        return False

    # the larger of the 2 x or y values will be added to and the smaller will
    # be subtracted from by the number robotSize
    def accountForRobotSize(self, p1, p2):
        ps = [p1, p2]
        if p1 < p2:
            ps[0] = p1 - self.robotSize
            ps[1] = p2 + self.robotSize 
        else:
            ps[0] = p1 + self.robotSize
            ps[1] = p2 - self.robotSize 
        return ps

class LineSegment:

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.lineAngle = math.degrees(math.atan2((y1 - y2), (x1 - x2)))
        if (self.lineAngle < 95 and self.lineAngle > 85) or (self.lineAngle < 275 and self.lineAngle > 265):
            self.x2 = self.x1
        if x1 - x2 != 0:
            self.m = (y1 - y2) / (x1 - x2)
            self.b = self.m * x1 - y1
        else:
            self.m = None
            self.b = None
        

    def collision(self, LineSegment):
        if self.m == LineSegment.m:# if lines are parallel
            return False
        elif self.m == None:
            # if one line is straight up
            if self.isBetween(LineSegment.x1, LineSegment.x2, self.x1) \
                and self.isBetween(self.y1, self.y2, (LineSegment.y1 + LineSegment.m * (self.x1 - LineSegment.x1))):
                return True
        elif LineSegment.m == None:
            # if the other line is straight up, figured out by finding the
            # change in x from an end on the non vertical line to the x value
            # of the vertical one. this is then multiplied by the slope of the
            # non vertical one and then added to the y value of the same end on
            # the non vertical one as before, to get the y value on the non
            # vertical line that has the same x as the vertical one. if that
            # is between the y values on the vertical line, they intersect.
            if self.isBetween(self.x1, self.x2, LineSegment.x1) \
                and self.isBetween(LineSegment.y1, LineSegment.y2, (self.y1 + self.m * (LineSegment.x1 - self.x1))):
                return True
        elif self.isBetween(self.x1, self.x2, ((self.b - LineSegment.b) / (self.m - LineSegment.m))) \
            and self.isBetween(self.y1, self.y2, ((self.b - LineSegment.b) / (self.m - LineSegment.m)) * self.m + self.b):
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

obstacles = [
    Obstacle(-26.8,-6.2,-18.8,6.2), # left hab
    Obstacle(-26.8,-7.5,-22.8,7.5), # left depot
    Obstacle(-10.3,-13.3,-5.5,-10.7), # bottom left rocket
    Obstacle(-10.3,10.7,-5.5,13.3), # top left rocket
    Obstacle(-8.6,-2.2,8.6,2.2), # cargo ship
    Obstacle(5.5,-13.3,10.3,-10.7), # bottom right rocket
    Obstacle(5.5,10.7,10.3,13.3), # top right rocket
    Obstacle(18.8,-6.2,26.8,6.2), # right hab
    Obstacle(22.8,-7.5,26.8,7.5) ] # right depot

def testCollision(x1, y1, x2, y2):
    robotPath = LineSegment(x1,y1,x2,y2)
    for obstacle in obstacles:
        if obstacle.detectCollision(robotPath):
            return True
    return False