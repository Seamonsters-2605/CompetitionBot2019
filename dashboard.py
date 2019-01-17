import remi.gui as gui
import seamonsters as sea

class CompetitionBotDashboard(sea.Dashboard):

    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.VBox(width=600)

        self.encoderPositionLbl = gui.Label("[encoder position]")
        root.append(self.encoderPositionLbl)
        self.navxPositionLbl = gui.Label("[navx position]")
        root.append(self.navxPositionLbl)
        self.visionPositionLbl = gui.Label("[vision position]")
        root.append(self.visionPositionLbl)

        zeroSteeringBtn = gui.Button("Reset swerve rotations")
        zeroSteeringBtn.onclick.connect(self.queuedEvent(robot.c_zeroSteering))
        root.append(zeroSteeringBtn)

        zeroPosition = gui.Button("Reset position")
        zeroPosition.onclick.connect(self.queuedEvent(robot.c_zeroPosition))
        root.append(zeroPosition)

        self.driveGearLbl = gui.Label("[drive gear]")
        root.append(self.driveGearLbl)

        voltageModeBox = gui.HBox()
        root.append(voltageModeBox)
        slowVoltageBtn = gui.Button("[Slow Voltage]")
        slowVoltageBtn.onclick.connect(self.queuedEvent(robot.c_slowVoltageGear))
        voltageModeBox.append(slowVoltageBtn)
        mediumVoltageBtn = gui.Button("[Medium Voltage]")
        mediumVoltageBtn.onclick.connect(self.queuedEvent(robot.c_mediumVoltageGear))
        voltageModeBox.append(mediumVoltageBtn)
        fastVoltageBtn = gui.Button("[Fast Voltage]")
        fastVoltageBtn.onclick.connect(self.queuedEvent(robot.c_fastVoltageGear))
        voltageModeBox.append(fastVoltageBtn)

        velocityModeBox = gui.HBox()
        root.append(velocityModeBox)
        slowVelocityBtn = gui.Button("[Slow Velocity]")
        slowVelocityBtn.onclick.connect(self.queuedEvent(robot.c_slowVelocityGear))
        velocityModeBox.append(slowVelocityBtn)
        mediumVelocityBtn = gui.Button("[Medium Velocity]")
        mediumVelocityBtn.onclick.connect(self.queuedEvent(robot.c_mediumVelocityGear))
        velocityModeBox.append(mediumVelocityBtn)
        fastVelocityBtn = gui.Button("[Fast Velocity]")
        fastVelocityBtn.onclick.connect(self.queuedEvent(robot.c_fastVelocityGear))
        velocityModeBox.append(fastVelocityBtn)

        appCallback(self)
        return root
