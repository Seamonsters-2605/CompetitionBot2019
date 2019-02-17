class DriveGear:

    def __init__(self, name, mode, moveScale, turnScale,
                 p=0.0, i=0.0, d=0.0, f=0.0, realTime=True):
        self.name = name
        self.mode = mode
        self.moveScale = moveScale
        self.turnScale = turnScale
        self.p = p
        self.i = i
        self.d = d
        self.f = f
        self.realTime = realTime

    def __repr__(self):
        return self.name

    def applyGear(self, superDrive):
        if superDrive.gear == self:
            return False
        print("Set gear to", self)
        superDrive.gear = self # not a normal property of the superDrive
        for wheel in superDrive.wheels:
            wheel.angledWheel.driveMode = self.mode
            wheel.angledWheel.realTime = self.realTime
            wheelMotor = wheel.angledWheel.motor
            wheelMotor.config_kP(0, self.p, 0)
            wheelMotor.config_kI(0, self.i, 0)
            wheelMotor.config_kD(0, self.d, 0)
            wheelMotor.config_kF(0, self.f, 0)
        return True
