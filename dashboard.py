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

        addActionAtIndexBox = gui.HBox()
        addActionAtIndexButton = gui.Button('Add action at index: ')
        self.indexInput = gui.Input()
        addActionAtIndexButton.onclick.connect(self.queuedEvent(robot.c_addActionAtIndex))
        addActionAtIndexBox.append(addActionAtIndexButton)
        addActionAtIndexBox.append(self.indexInput)

        controlBox = gui.HBox()
        schedulerBox.append(addActionAtIndexBox)
        schedulerBox.append(controlBox)

        pauseButton = gui.Button('Pause')
        pauseButton.onclick.connect(self.queuedEvent(robot.c_pauseScheduler))
        controlBox.append(pauseButton)
        resumeButton = gui.Button('Resume')
        resumeButton.onclick.connect(self.queuedEvent(robot.c_resumeScheduler))
        controlBox.append(resumeButton)

        schedulerBox.append(gui.Label("Schedule:"))

        self.schedulerList = gui.ListView()
        self.schedulerList.set_on_selection_listener(self.listViewCallback)
        
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

    def listViewCallback(self,listView,*args):
        for num,value in enumerate(listView.children.values()):
            # if value is listView.get_item() , get num. num is index
            if value == listView.get_item():
                removeItemIndex = num
                break
        scheduler = self.robot.autoScheduler.actionList 
        print(scheduler)
        print(removeItemIndex)

        if removeItemIndex > 0 and removeItemIndex < len(scheduler):
            listView.remove_child(listView.get_item())
            scheduler.remove(scheduler[removeItemIndex])
        if removeItemIndex == len(scheduler):
            listView.remove_child(listView.get_item())
            scheduler.clear()
        print('remove',removeItemIndex)
        
    # def addActionAtIndex(self)
    

