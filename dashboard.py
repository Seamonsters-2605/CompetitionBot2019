import math
import remi.gui as gui
import seamonsters as sea

class CompetitionBotDashboard(sea.Dashboard):

    FIELD_WIDTH = 500
    FIELD_HEIGHT = 450
    FIELD_PIXELS_PER_FOOT = 10

    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.VBox(width=600)

        self.realTimeRatioLbl = gui.Label("[real time ratio]")
        root.append(self.realTimeRatioLbl)

        self.currentLbl = gui.Label("[current]")
        root.append(self.currentLbl)

        self.robotPositionLbl = gui.Label("[robot position]")
        root.append(self.robotPositionLbl)

        zeroSteeringBtn = gui.Button("Reset swerve rotations")
        zeroSteeringBtn.onclick.connect(robot.c_wheelsToZero)
        root.append(zeroSteeringBtn)

        zeroPosition = gui.Button("Reset position")
        zeroPosition.onclick.connect(robot.c_zeroPosition)
        root.append(zeroPosition)

        self.driveGearLbl = gui.Label("[drive gear]")
        root.append(self.driveGearLbl)

        root.append(self.initGearSelector(robot))

        root.append(self.initFieldMap())
        self.updateRobotPosition(0, 0, 0)

        root.append(self.initScheduler(robot))
        self.updateScheduler()

        appCallback(self)
        return root

    def initGearSelector(self, robot):
        gearSelectorBox = gui.VBox()

        voltageModeBox = gui.HBox()
        gearSelectorBox.append(voltageModeBox)
        slowVoltageBtn = gui.Button("[Slow Voltage]")
        slowVoltageBtn.onclick.connect(robot.c_slowVoltageGear)
        voltageModeBox.append(slowVoltageBtn)
        mediumVoltageBtn = gui.Button("[Medium Voltage]")
        mediumVoltageBtn.onclick.connect(robot.c_mediumVoltageGear)
        voltageModeBox.append(mediumVoltageBtn)
        fastVoltageBtn = gui.Button("[Fast Voltage]")
        fastVoltageBtn.onclick.connect(robot.c_fastVoltageGear)
        voltageModeBox.append(fastVoltageBtn)

        velocityModeBox = gui.HBox()
        gearSelectorBox.append(velocityModeBox)
        slowVelocityBtn = gui.Button("[Slow Position]")
        slowVelocityBtn.onclick.connect(robot.c_slowPositionGear)
        velocityModeBox.append(slowVelocityBtn)
        mediumVelocityBtn = gui.Button("[Medium Position]")
        mediumVelocityBtn.onclick.connect(robot.c_mediumPositionGear)
        velocityModeBox.append(mediumVelocityBtn)
        fastVelocityBtn = gui.Button("[Fast Position]")
        fastVelocityBtn.onclick.connect(robot.c_fastPositionGear)
        velocityModeBox.append(fastVelocityBtn)

        return gearSelectorBox

    def initFieldMap(self):
        self.fieldSvg = gui.Svg(CompetitionBotDashboard.FIELD_WIDTH,
            CompetitionBotDashboard.FIELD_HEIGHT)

        self.arrow = gui.SvgPolyline()
        self.fieldSvg.append(self.arrow)
        self.arrow.add_coord(0, 0)
        self.arrow.add_coord(10, 40)
        self.arrow.add_coord(-10, 40)
        self.arrow.style['fill'] = 'gray'

        return self.fieldSvg

    def initScheduler(self, robot):
        schedulerBox = gui.VBox()

        addActionBox = gui.VBox()
        addActionBox.append(gui.Label("Add Action:"))
        schedulerBox.append(addActionBox)

        waitActionBox = gui.HBox()
        addActionBox.append(waitActionBox)
        addWaitActionBtn = gui.Button('Wait')
        addWaitActionBtn.onclick.connect(robot.c_addWaitAction)
        waitActionBox.append(addWaitActionBtn)
        self.waitTimeInput = gui.Input()
        waitActionBox.append(self.waitTimeInput)

        driveToPointActionBox = gui.HBox()
        addActionBox.append(driveToPointActionBox)
        addDriveToPointActionBtn = gui.Button('Drive to Point')
        addDriveToPointActionBtn.onclick.connect(robot.c_addDriveToPointAction)
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
        pauseButton.onclick.connect(robot.c_pauseScheduler)
        controlBox.append(pauseButton)
        resumeButton = gui.Button('Resume')
        resumeButton.onclick.connect(robot.c_resumeScheduler)
        controlBox.append(resumeButton)

        schedulerBox.append(gui.Label("Schedule:"))

        self.schedulerList = gui.ListView()
        schedulerBox.append(self.schedulerList)

        return schedulerBox

    def updateRobotPosition(self, robotX, robotY, robotAngle):
        self.robotPositionLbl.set_text('%.3f, %.3f, %.3f' %
            (robotX, robotY, math.degrees(robotAngle)))

        arrowX = CompetitionBotDashboard.FIELD_WIDTH / 2
        arrowX += robotX * CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT
        arrowY = CompetitionBotDashboard.FIELD_HEIGHT / 2
        arrowY -= robotY * CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT
        arrowAngle = -math.degrees(robotAngle)
        self.arrow.attributes['transform'] = "translate(%s,%s) rotate(%s)" \
            % (arrowX, arrowY, arrowAngle)
    
    def updateScheduler(self):
        scheduler = self.robot.autoScheduler
        self.schedulerList.empty()
        if scheduler.runningAction is not None:
            runningItem = gui.ListItem('* ' + scheduler.runningAction.name)
            self.schedulerList.append(runningItem)
        for action in scheduler.actionList:
            listItem = gui.ListItem(action.name)
            self.schedulerList.append(listItem)
