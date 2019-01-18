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

        root.append(self.initScheduler(robot))
        self.updateScheduler()

        appCallback(self)
        return root

    def initScheduler(self, robot):
        schedulerBox = gui.VBox()

        addActionBox = gui.VBox()
        addActionBox.append(gui.Label("Add Action:"))
        schedulerBox.append(addActionBox)

        waitActionBox = gui.HBox()
        addActionBox.append(waitActionBox)
        addWaitActionBtn = gui.Button('Wait')
        addWaitActionBtn.onclick.connect(self.queuedEvent(robot.c_addWaitAction))
        waitActionBox.append(addWaitActionBtn)
        self.waitTimeInput = gui.Input()
        waitActionBox.append(self.waitTimeInput)

        driveToPointActionBox = gui.HBox()
        addActionBox.append(driveToPointActionBox)
        addDriveToPointActionBtn = gui.Button('Drive to Point')
        addDriveToPointActionBtn.onclick.connect(self.queuedEvent(robot.c_addDriveToPointAction))
        driveToPointActionBox.append(addDriveToPointActionBtn)
        self.pointXInput = gui.Input()
        driveToPointActionBox.append(self.pointXInput)
        self.pointYInput = gui.Input()
        driveToPointActionBox.append(self.pointYInput)
        self.pointAngleInput = gui.Input()
        driveToPointActionBox.append(self.pointAngleInput)

        controlBox = gui.HBox()
        schedulerBox.append(controlBox)

        pauseButton = gui.Button('Pause')
        pauseButton.onclick.connect(self.queuedEvent(robot.c_pauseScheduler))
        controlBox.append(pauseButton)
        resumeButton = gui.Button('Resume')
        resumeButton.onclick.connect(self.queuedEvent(robot.c_resumeScheduler))
        controlBox.append(resumeButton)

        schedulerBox.append(gui.Label("Schedule:"))

        self.schedulerList = gui.ListView()
        schedulerBox.append(self.schedulerList)

        return schedulerBox
    
    def updateScheduler(self):
        scheduler = self.robot.autoScheduler
        self.schedulerList.empty()
        if scheduler.runningAction is not None:
            runningItem = gui.ListItem('* ' + scheduler.runningAction.name)
            self.schedulerList.append(runningItem)
        for action in scheduler.actionList:
            listItem = gui.ListItem(action.name)
            self.schedulerList.append(listItem)
