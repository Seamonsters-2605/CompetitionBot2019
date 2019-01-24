import math
import remi.gui as gui
import seamonsters as sea

class CompetitionBotDashboard(sea.Dashboard):

    # these values match the simulator config.json and the field image
    FIELD_WIDTH = 540
    FIELD_HEIGHT = 270
    FIELD_PIXELS_PER_FOOT = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, css=True, **kwargs)

    # apply a style to the widget to visually group items together
    def groupStyle(self, widget):
        widget.style['border'] = '2px solid gray'
        widget.style['border-radius'] = '0.5em'
        widget.style['margin'] = '0.5em'
        widget.style['padding'] = '0.2em'

    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.VBox(width=600, margin='0px auto')

        closeButton = gui.Button("Close")
        closeButton.onclick.connect(self.c_closeApp)
        root.append(closeButton)

        self.click_Cursor = (0,0)

        self.realTimeRatioLbl = gui.Label("[real time ratio]")
        root.append(self.realTimeRatioLbl)

        self.currentLbl = gui.Label("[current]")
        root.append(self.currentLbl)

        zeroSteeringBtn = gui.Button("Reset swerve rotations")
        zeroSteeringBtn.onclick.connect(robot.c_wheelsToZero)
        root.append(zeroSteeringBtn)

        root.append(self.initGearSelector(robot))

        root.append(self.initFieldMap(robot))
        self.updateRobotPosition(0, 0, 0)

        root.append(self.initScheduler(robot))
        self.updateScheduler()

        appCallback(self)
        return root

    def initGearSelector(self, robot):
        gearSelectorBox = gui.VBox()
        self.groupStyle(gearSelectorBox)

        self.driveGearLbl = gui.Label("[drive gear]")
        gearSelectorBox.append(self.driveGearLbl)

        voltageModeBox = gui.HBox()
        gearSelectorBox.append(voltageModeBox)
        slowVoltageBtn = gui.Button("Slow Voltage")
        slowVoltageBtn.onclick.connect(robot.c_slowVoltageGear)
        voltageModeBox.append(slowVoltageBtn)
        mediumVoltageBtn = gui.Button("Medium Voltage")
        mediumVoltageBtn.onclick.connect(robot.c_mediumVoltageGear)
        voltageModeBox.append(mediumVoltageBtn)
        fastVoltageBtn = gui.Button("Fast Voltage")
        fastVoltageBtn.onclick.connect(robot.c_fastVoltageGear)
        voltageModeBox.append(fastVoltageBtn)

        velocityModeBox = gui.HBox()
        gearSelectorBox.append(velocityModeBox)
        slowVelocityBtn = gui.Button("Slow Position")
        slowVelocityBtn.onclick.connect(robot.c_slowPositionGear)
        velocityModeBox.append(slowVelocityBtn)
        mediumVelocityBtn = gui.Button("Medium Position")
        mediumVelocityBtn.onclick.connect(robot.c_mediumPositionGear)
        velocityModeBox.append(mediumVelocityBtn)
        fastVelocityBtn = gui.Button("Fast Position")
        fastVelocityBtn.onclick.connect(robot.c_fastPositionGear)
        velocityModeBox.append(fastVelocityBtn)

        return gearSelectorBox

    def initFieldMap(self, robot):

        fieldBox = gui.VBox()
        self.groupStyle(fieldBox)

        posBox = gui.HBox()
        fieldBox.append(posBox)

        self.robotPositionLbl = gui.Label("[robot position]")
        posBox.append(self.robotPositionLbl)

        zeroPosition = gui.Button("Reset position")
        zeroPosition.onclick.connect(robot.c_zeroPosition)
        posBox.append(zeroPosition)

        fieldSvg = gui.Svg(CompetitionBotDashboard.FIELD_WIDTH,
        CompetitionBotDashboard.FIELD_HEIGHT)
        fieldSvg.set_on_mousedown_listener(self.mouse_down_listener)
        fieldBox.append(fieldSvg)
        

        self.image = gui.SvgShape(0, 0)
        self.image.type = 'image'
        self.image.attributes['width'] = CompetitionBotDashboard.FIELD_WIDTH
        self.image.attributes['height'] = CompetitionBotDashboard.FIELD_HEIGHT
        self.image.attributes['xlink:href'] = '/res:frcField.PNG'
        fieldSvg.append(self.image)

        self.arrow = gui.SvgPolyline()
        self.arrow.add_coord(0, 0)
        self.arrow.add_coord(10, 40)
        self.arrow.add_coord(-10, 40)
        self.arrow.style['fill'] = 'green'
        fieldSvg.append(self.arrow)

        return fieldBox
    
    def mouse_down_listener(self,widget,x,y):
        self.click_Cursor = (x,y)
        self.pointXInput.set_value(self.svgToFieldCordinates(x,y)[0])
        self.pointYInput.set_value(self.svgToFieldCordinates(x,y)[1])
        print(x,y)

    def initScheduler(self, robot):
        schedulerBox = gui.VBox()
        self.groupStyle(schedulerBox)

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
    
    def svgToFieldCordinates(self,x,y):
        return ( (float(x) - CompetitionBotDashboard.FIELD_WIDTH  / 2) / CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT,
                -(float(y) - CompetitionBotDashboard.FIELD_HEIGHT / 2) / CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT)
    
    def updateScheduler(self):
        scheduler = self.robot.autoScheduler
        self.schedulerList.empty()
        if scheduler.runningAction is not None:
            runningItem = gui.ListItem('* ' + scheduler.runningAction.name)
            self.schedulerList.append(runningItem)
        for action in scheduler.actionList:
            listItem = gui.ListItem(action.name)
            self.schedulerList.append(listItem)

    def c_closeApp(self, button):
        self.close()
