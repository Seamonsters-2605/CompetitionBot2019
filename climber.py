import wpilib
import ctre
import seamonsters as sea

class Climber:

    def __init__(self):
        self.motor1 = ctre.WPI_TalonSRX(31)
        self.motor1.configFactoryDefault(0)
        self.motor1.setNeutralMode(ctre.NeutralMode.Brake)
        self.motor2 = ctre.WPI_TalonSRX(32)
        self.motor2.configFactoryDefault(0)
        self.motor2.setNeutralMode(ctre.NeutralMode.Brake)
        self.fast = False

    def climb(self, speed):
        if self.fast:
            self.motor1.set(speed * -1)
            self.motor2.set(speed * -1)
        else:
            self.motor1.set(speed * -.8)
            self.motor2.set(speed * -.8)
