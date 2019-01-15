class DriveCoordinates

    def __init__(self, name, x_coordinate, y_coordinate, orientation)

        self.name = name
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.orientation = orientation

rocket1 = DriveCoordinates("Rocket1", 6, 12, math.radians(-135))
rocket2 = DriveCoordinates("Rocket2", 7.5, 10.5, math.radians(-90))
rocket3 = DriveCoordinates("Rocket3", 9, 12, math.radians(-45))
waypoint1 = DriveCoordinates("Waypoint1", 3, 7.5, math.radians(0))
waypoint2 = DriveCoordinates("Waypoint2", 15, 7.5, math.radians(0))
waypoint3 = DriveCoordinates("Waypoint3", 15, 0, math.radians(0))
humanstation1 = DriveCoordinates("human1", 27, 10.8, math.radians(180))
