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

        self.driveGearLbl = gui.Label("[drive gear]")
        root.append(self.driveGearLbl)

        driveModeBox = gui.HBox()
        root.append(driveModeBox)

        slowBtn = gui.Button("Slow")
        slowBtn.onclick.connect(self.queuedEvent(robot.slow))
        driveModeBox.append(slowBtn)
        mediumBtn = gui.Button("Medium")
        mediumBtn.onclick.connect(self.queuedEvent(robot.medium))
        driveModeBox.append(mediumBtn)
        fastBtn = gui.Button("Fast")
        fastBtn.onclick.connect(self.queuedEvent(robot.fast))
        driveModeBox.append(fastBtn)

        root.append(self.initScheduler(robot))
        self.updateScheduler()

        appCallback(self)
        return root

    def initScheduler(self, robot):
        schedulerBox = gui.VBox()

        testActionButton = gui.Button('Test Action')
        testActionButton.onclick.connect(self.queuedEvent(robot.c_testAction))
        schedulerBox.append(testActionButton)

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
