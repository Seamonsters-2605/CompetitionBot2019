import math


def circleDistance(a, b):
    diff = a - b
    while diff > math.pi:
        diff -= math.pi * 2
    while diff < -math.pi:
        diff += math.pi * 2
    return diff


class DriveCoordinates:

    def __init__(self, name, x_coordinate, y_coordinate, orientation):
        self.name = name
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.orientation = orientation
        self.angle = math.atan2(self.y_coordinate, self.x_coordinate)

rocket1 = DriveCoordinates("Rocket1", 6, 12, math.radians(-135))
rocket2 = DriveCoordinates("Rocket2", 7.5, 10.5, math.radians(-90))
rocket3 = DriveCoordinates("Rocket3", 9, 12, math.radians(-45))
waypoint1 = DriveCoordinates("Waypoint1", 15, 0, math.radians(0))
waypoint2 = DriveCoordinates("Waypoint2", 15, 7.5, math.radians(0))
waypoint3 = DriveCoordinates("Waypoint3", -15, 7.5, math.radians(0))
waypoint4 = DriveCoordinates("Waypoint4", -15, 0, math.radians(0))
waypoint5 = DriveCoordinates("Waypoint5", -15, -7.5, math.radians(0))
waypoint6 = DriveCoordinates("Waypoint6", 15, -7.5, math.radians(0))
humanstation1 = DriveCoordinates("human1", 27, 10.8, math.radians(180))
# in counterclockwise order
waypoints = [waypoint1, waypoint2, waypoint3, waypoint4, waypoint5, waypoint6]

def findWaypoints(targetCoord, robotX, robotY):
    robotAngle = math.atan2(robotY, robotX)
    
    nearestCWWaypoint = 0
    while nearestCWWaypoint < len(waypoints):
        point = waypoints[nearestCWWaypoint]
        if circleDistance(robotAngle, point.angle) < 0:
            break
        nearestCWWaypoint += 1
    nearestCWWaypoint %= len(waypoints)

    moveClockwise = circleDistance(robotAngle, targetCoord.angle) > 0

    pointI = nearestCWWaypoint
    if moveClockwise:
        pointI += 1
        pointI %= len(waypoints)

    path = []

    while True:
        waypoint = waypoints[pointI]
        clockwiseFromWaypoint = circleDistance(waypoint.angle, targetCoord.angle) > 0
        if clockwiseFromWaypoint == moveClockwise:
            print("Point", pointI)
            path.append(waypoint)
        else:
            break
        if moveClockwise:
            pointI -= 1 # negative indices are fine
        else:
            pointI += 1

    path.append(targetCoord)
    return path
