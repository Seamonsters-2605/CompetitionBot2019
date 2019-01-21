import math


def circleDistance(self, a, b):
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
waypoints = [waypoint1, waypoint2, waypoint3, waypoint4, waypoint5, waypoint6]

def waypointss(driveCoord, x, y):
    meangle = math.atan2(y,x)
    waypoint = None
    Direc = None
    yote = self.circleDistance(meangle, math.atan2(driveCoord.y_coordinate, driveCoord.x_coordinate))
    driveDir = []
    way1

    if yote > 0:
        print ("counterclockwise")
        Direc = True
        print(Direc)
    else:
        print("clockwise")
        Direc = False
        print(Direc)
    if meangle < waypoint1.angle:
        waypoint = (5,0)
        print(waypoint)
    elif meangle < waypoint2.angle:
        waypoint = (0,1)
        print(waypoint)
    elif meangle < waypoint3.angle:
        waypoint = (1,2)
        print(waypoint)
    elif meangle < waypoint4.angle:
        waypoint = (2,3)
        print(waypoint)
    elif meangle < waypoint5.angle:
        waypoint = (3,4)
        print(waypoint)
    else:
        waypoint = (4,5)
        print(waypoint)
    
    if Direc == True:
        way1 = waypoint[0]
        print(way1)
    else:
        way1 = waypoint[1]
        print(way1)
    driveDir.append(way1)
    for x in waypoints:
        if Direc == True:
            if waypoints.angle > meangle:
                driveDir.append(waypoints[way1+1])
                print (driveDir)
            else:
                print(meangle)
                print(driveDir)
                
        elif Direc == False:
            if waypoints.angle < meangle:
                driveDir.append(waypoints[way1+1])
                print(driveDir)
            else:
                print (meangle)
                print(driveDir)
                