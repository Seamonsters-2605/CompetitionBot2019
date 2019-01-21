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
waypoints = [waypoint1, waypoint2, waypoint3, waypoint4, waypoint5, waypoint6]

def findWaypoints(driveCoord, x, y):
    meangle = math.atan2(y,x)
    goat = circleDistance(meangle, math.atan2(driveCoord.y_coordinate, driveCoord.x_coordinate))
    drivePoints = []
    if goat > 0:
        print ("counterclockwise")
        Direc = True
    else:
        print("clockwise")
        Direc = False
       
    if meangle < waypoint1.angle:
        surround = (5,0)
    elif meangle < waypoint2.angle:
        surround = (0,1)
    elif meangle < waypoint3.angle:
        surround = (1,2)
    elif meangle < waypoint4.angle:
        surround = (2,3)
    elif meangle < waypoint5.angle:
        surround = (3,4)
    elif meangle < waypoint6.angle:
        surround = (4,5)
    else:
        surround = (5,0)
    print(surround)
    
    if Direc == True:
        way1 = surround[0]
        print(way1)
    else:
        way1 = surround[1]
        print(way1)
    drivePoints.append(way1)
    for dRiVePoInT in waypoints:
        if Direc == True:
            if dRiVePoInT.angle > meangle:
                drivePoints.append(waypoints[way1+1])
                print (drivePoints)
            else:
                print(meangle)
                print(drivePoints)
                
        elif Direc == False:
            if dRiVePoInT.angle < meangle:
                drivePoints.append(waypoints[way1+1])
                print(drivePoints)
            else:
                print (meangle)
                print(drivePoints)
    return drivePoints