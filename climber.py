import wpilib
import ctre
import seamonsters as sea

class Climber:

    def __init__(self):
        self.motor1 = ctre.WPI_TalonSRX(31)
        self.motor1.setNeutralMode(ctre.NeutralMode.Brake)
        self.motor2 = ctre.WPI_TalonSRX(32)
        self.motor2.setNeutralMode(ctre.NeutralMode.Brake)

    def climb(self, speed):
        self.motor1.set(speed * .5)
        self.motor2.set(speed * .5)
