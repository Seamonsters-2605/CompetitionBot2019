import math
import remi.gui as gui
import seamonsters as sea
import coordinates
import drivetrain
import auto_actions
import random

def svgToFieldCoordinates(x, y):
    return ( (float(x) - CompetitionBotDashboard.FIELD_WIDTH  / 2) / CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT,
            (-float(y) + CompetitionBotDashboard.FIELD_HEIGHT / 2) / CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT)

def fieldToSvgCoordinates(x, y):
    return (CompetitionBotDashboard.FIELD_WIDTH  / 2 + x * CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT,
            CompetitionBotDashboard.FIELD_HEIGHT / 2 - y * CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT)

class Arrow(gui.SvgPolyline):

    def __init__(self, color):
        super().__init__()
        halfWidth = drivetrain.ROBOT_WIDTH * CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT / 2
        halfLength = drivetrain.ROBOT_LENGTH * CompetitionBotDashboard.FIELD_PIXELS_PER_FOOT / 2
        self.add_coord(0, -halfLength)
        self.add_coord(halfWidth, halfLength)
        self.add_coord(-halfWidth, halfLength)
        self.style['fill'] = color
        self.setPosition(0, 0, 0)

    def setPosition(self, x, y, angle=None):
        self.x = x
        self.y = y
        if angle is not None:
            self.angle = angle
        else:
            angle = self.angle

        svgX, svgY = fieldToSvgCoordinates(x, y)
        svgAngle = -math.degrees(angle)
        self.attributes['transform'] = "translate(%s,%s) rotate(%s)" \
            % (svgX, svgY, svgAngle)


class WheelButtonController:

    def __init__(self, num, wheel, robot):
        self.num = num
        self.wheel = wheel
        self.name = chr(ord('A') + num)
        self.button = gui.Button(self.name)
        self._buttonColor("green")
        self.button.controller = self
        self.button.onclick.connect(robot.c_wheelButtonClicked)
        self.encoderWorking = True

    def _buttonColor(self, color):
        self.button.style["background"] = color

    def update(self):
        if self.wheel.disabled:
            return
        if self.encoderWorking and not self.wheel.encoderWorking:
            self._buttonColor("red")
        elif self.wheel.encoderWorking and not self.encoderWorking:
            self._buttonColor("green")

    def clicked(self):
        if not self.wheel.disabled:
            self.wheel.disabled = True
            self._buttonColor("black")
        else:
            self.wheel.disabled = False
            self.wheel.encoderWorking = True
            self.encoderWorking = True
            self._buttonColor("green")

class CompetitionBotDashboard(sea.Dashboard):

    # these values match the simulator config.json and the field image
    FIELD_WIDTH = 540
    FIELD_HEIGHT = 270
    FIELD_PIXELS_PER_FOOT = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, css=True, **kwargs)

    # apply a style to the widget to visually group items together
    def sectionBox(self):
        vbox = gui.VBox()
        vbox.style['border'] = '2px solid gray'
        vbox.style['border-radius'] = '0.5em'
        vbox.style['margin'] = '0.5em'
        vbox.style['padding'] = '0.2em'
        return vbox

    def spaceBox(self):
        return gui.HBox(width=10)

    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.VBox(width=600, margin='0px auto')

        root.append(self.initGeneral(robot))
        root.append(self.initManualControls(robot))
        root.append(self.initWheelControls(robot))

        root.append(self.initFieldMap(robot))
        self.selectedCoord = coordinates.DriveCoordinate("Center", 0, 0, math.radians(-90))
        self.updateCursorPosition()

        root.append(self.initScheduler(robot))
        self.updateScheduler()
        self.updateSchedulerFlag = False

        root.append(self.initTestControl(robot))

        appCallback(self)
        return root

    def idle(self):
        pf = self.robot.pathFollower
        self.updateRobotPosition(
            pf.robotX, pf.robotY, pf.robotAngle)
        self.realTimeRatioLbl.set_text(
            '%.3f' % (self.robot.timingMonitor.realTimeRatio,))
        for wheelButton in self.wheelBtns:
            wheelButton.update()

        if self.updateSchedulerFlag:
            self.updateScheduler()
            self.updateSchedulerFlag = False

    def initGeneral(self, robot):
        generalBox = self.sectionBox()

        dashboardBox = gui.HBox()
        generalBox.append(dashboardBox)

        closeButton = gui.Button("Close")
        closeButton.onclick.connect(self.c_closeApp)
        dashboardBox.append(closeButton)

        connectionTestButton = gui.Button("Connection Test")
        dashboardBox.append(connectionTestButton)
        def connectionTest(button):
            color = "rgb(%d, %d, %d)" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            connectionTestButton.style["background"] = color
        connectionTestButton.onclick.connect(connectionTest)

        self.realTimeRatioLbl = gui.Label("[real time ratio]")
        generalBox.append(self.realTimeRatioLbl)

        return generalBox

    def initManualControls(self, robot):
        manualBox = self.sectionBox()
        manualBox.append(gui.Label("MANUAL"))

        clawModeBox = gui.HBox()
        manualBox.append(clawModeBox)

        auxDisabledBtn = gui.Button("No Aux")
        auxDisabledBtn.onclick.connect(robot.c_auxDisabledMode)
        clawModeBox.append(auxDisabledBtn)

        defenseButton = gui.Button("Defense Mode")
        defenseButton.onclick.connect(robot.c_defenseMode)
        clawModeBox.append(defenseButton)

        cargoButton = gui.Button("Cargo Mode")
        cargoButton.onclick.connect(robot.c_cargoMode)
        clawModeBox.append(cargoButton)
        
        hatchButton = gui.Button("Hatch Mode")
        hatchButton.onclick.connect(robot.c_hatchMode)
        clawModeBox.append(hatchButton)

        climbBtn = gui.Button("Climb Mode")
        climbBtn.onclick.connect(robot.c_climbMode)
        clawModeBox.append(climbBtn)

        self.driveGearLbl = gui.Label("[drive gear]")
        manualBox.append(self.driveGearLbl)

        voltageModeBox = gui.HBox()
        manualBox.append(voltageModeBox)
        driveVoltageBtn = gui.Button("Drive Voltage")
        driveVoltageBtn.onclick.connect(robot.c_driveVoltage)
        voltageModeBox.append(driveVoltageBtn)
        drivePositionBtn = gui.Button("Drive Position")
        drivePositionBtn.onclick.connect(robot.c_drivePosition)
        voltageModeBox.append(drivePositionBtn)

        return manualBox

    def initWheelControls(self, robot):
        wheelControlsBox = self.sectionBox()
        wheelControlsBox.append(gui.Label("Swerve Wheels"))

        grid = gui.GridBox()
        grid.define_grid([['C','D'],['A','B']])
        wheelControlsBox.append(grid)

        self.wheelBtns = []
        for wheelIndex in range(4):
            newButton = WheelButtonController(wheelIndex,
                robot.superDrive.wheels[wheelIndex].angledWheel, robot)
            grid.append(newButton.button, newButton.name)
            self.wheelBtns.append(newButton)

        return wheelControlsBox

    def initFieldMap(self, robot):
        fieldBox = self.sectionBox()

        posBox = gui.HBox()
        fieldBox.append(posBox)

        posBox.append(gui.Label("Robot:"))
        posBox.append(self.spaceBox())
        self.robotPositionLbl = gui.Label('')
        posBox.append(self.robotPositionLbl)
        posBox.append(self.spaceBox())

        setPositionBtn = gui.Button("Set robot")
        setPositionBtn.onclick.connect(self.c_setRobotPosition)
        posBox.append(setPositionBtn)

        cursorBox = gui.HBox()
        fieldBox.append(cursorBox)

        cursorBox.append(gui.Label("Cursor:"))
        cursorBox.append(self.spaceBox())
        self.cursorPositionLbl = gui.Label('')
        cursorBox.append(self.cursorPositionLbl)
        cursorBox.append(self.spaceBox())

        def setCursorAngle(button, angle):
            self.selectedCoord = self.selectedCoord.withOrientation(angle)
            self.updateCursorPosition()
        leftBtn = gui.Button('<')
        leftBtn.onclick.connect(setCursorAngle, math.radians(90))
        cursorBox.append(leftBtn)
        rightBtn = gui.Button('>')
        rightBtn.onclick.connect(setCursorAngle, math.radians(-90))
        cursorBox.append(rightBtn)
        upBtn = gui.Button('^')
        upBtn.onclick.connect(setCursorAngle, 0)
        cursorBox.append(upBtn)
        downBtn = gui.Button('v')
        downBtn.onclick.connect(setCursorAngle, math.radians(180))
        cursorBox.append(downBtn)

        self.fieldSvg = gui.Svg(CompetitionBotDashboard.FIELD_WIDTH,
            CompetitionBotDashboard.FIELD_HEIGHT)
        self.fieldSvg.set_on_mousedown_listener(self.mouse_down_listener)
        fieldBox.append(self.fieldSvg)

        self.image = gui.SvgShape(0, 0)
        self.image.type = 'image'
        self.image.attributes['width'] = CompetitionBotDashboard.FIELD_WIDTH
        self.image.attributes['height'] = CompetitionBotDashboard.FIELD_HEIGHT
        self.image.attributes['xlink:href'] = '/res:frcField.PNG'
        self.fieldSvg.append(self.image)

        self.targetPoints = coordinates.targetPoints
        for point in self.targetPoints:
            point = fieldToSvgCoordinates(point.x,point.y)
            wp_dot = gui.SvgCircle(point[0], point[1], 5)
            wp_dot.attributes['fill'] = 'blue'
            self.fieldSvg.append(wp_dot)

        self.cursorArrow = Arrow('red')
        self.fieldSvg.append(self.cursorArrow)

        self.robotArrow = Arrow('green')
        self.fieldSvg.append(self.robotArrow)

        self.robotPathLines = []

        return fieldBox
    
    def mouse_down_listener(self,widget,x,y):
        x, y = svgToFieldCoordinates(x, y)
        self.selectedCoord = coordinates.DriveCoordinate("Selected",
            x, y, self.selectedCoord.orientation)
        for point in self.targetPoints:
            if math.hypot(x - point.x, y - point.y) < 1:
                self.selectedCoord = point
        self.updateCursorPosition()

    def initScheduler(self, robot):
        schedulerBox = self.sectionBox()

        controlBox = gui.HBox()
        schedulerBox.append(controlBox)
        manualModeBtn = gui.Button("Manual")
        manualModeBtn.onclick.connect(robot.c_manualMode)
        controlBox.append(manualModeBtn)
        autoModeBtn = gui.Button("Auto")
        autoModeBtn.onclick.connect(robot.c_autoMode)
        controlBox.append(autoModeBtn)

        hbox = gui.HBox()
        hbox.style['align-items'] = 'flex-start'
        schedulerBox.append(hbox)

        addActionBox = gui.VBox()
        hbox.append(addActionBox)

        speedBox = gui.HBox()
        addActionBox.append(speedBox)
        speedBox.append(gui.Label("Speed:"))
        self.speedInput = gui.Input()
        self.speedInput.set_value("5")
        speedBox.append(self.speedInput)

        addActionBox.append(gui.Label("Auto actions:"))

        genericActionList = gui.ListView()
        genericActionList.append("Drive to Point", "drivetopoint")
        genericActionList.append("Navigate to Point", "navigatetopoint")
        genericActionList.append("Set robot position", "setposition")
        index = 0
        for action in robot.genericAutoActions:
            genericActionList.append(gui.ListItem(action.name), str(index))
            index += 1
        genericActionList.onselection.connect(self.c_addGenericAction)
        addActionBox.append(genericActionList)

        scheduleListBox = gui.VBox()
        hbox.append(scheduleListBox)
        clearScheduleBox = gui.HBox()
        scheduleListBox.append(clearScheduleBox)
        clearScheduleBox.append(gui.Label("Schedule:"))
        clearScheduleBtn = gui.Button("Clear")
        clearScheduleBtn.onclick.connect(self.c_clearSchedule)
        clearScheduleBox.append(clearScheduleBtn)

        self.schedulerList = gui.ListView()
        self.schedulerList.onselection.connect(self.c_removeAction)
        scheduleListBox.append(self.schedulerList)

        return schedulerBox

    def initTestControl(self, robot):
        testBox = self.sectionBox()
        testBox.append(gui.Label("TEST MODE"))

        compressorBox = gui.HBox()
        testBox.append(compressorBox)
        compressorBox.append(gui.Label("Compressor:"))
        startCompressorBtn = gui.Button("Start")
        startCompressorBtn.onclick.connect(robot.c_startCompressor)
        compressorBox.append(startCompressorBtn)
        stopCompressorBtn = gui.Button("Stop")
        stopCompressorBtn.onclick.connect(robot.c_stopCompressor)
        compressorBox.append(stopCompressorBtn)

        logBox = gui.HBox()
        testBox.append(logBox)

        logOpticalBtn = gui.Button("Log Optical")
        logOpticalBtn.onclick.connect(robot.c_logOpticalSensors)
        logBox.append(logOpticalBtn)

        logElevatorBtn = gui.Button("Log Elevator")
        logElevatorBtn.onclick.connect(robot.c_logElevator)
        logBox.append(logElevatorBtn)

        swerveBox = gui.HBox()
        testBox.append(swerveBox)

        homeSwerveBtn = gui.Button("Home swerve")
        homeSwerveBtn.onclick.connect(robot.c_homeSwerveWheels)
        swerveBox.append(homeSwerveBtn)

        resetSwerveBtn = gui.Button("Wheels to zero")
        resetSwerveBtn.onclick.connect(robot.c_wheelsToZero)
        swerveBox.append(resetSwerveBtn)

        setSwerveZeroBtn = gui.Button("Set swerve zero")
        setSwerveZeroBtn.onclick.connect(robot.c_setSwerveZero)
        swerveBox.append(setSwerveZeroBtn)

        resetClawBtn = gui.Button("Reset Claw")
        resetClawBtn.onclick.connect(robot.c_resetClaw)
        testBox.append(resetClawBtn)

        pidFrame = gui.HBox()
        testBox.append(pidFrame)
        pidTable = gui.VBox()
        pidFrame.append(pidTable)
        pidRow = gui.HBox()
        pidTable.append(pidRow)
        pIn = gui.Input()
        pidRow.append(pIn)
        iIn = gui.Input()
        pidRow.append(iIn)
        pidRow = gui.HBox()
        pidTable.append(pidRow)
        dIn = gui.Input()
        pidRow.append(dIn)
        fIn = gui.Input()
        pidRow.append(fIn)
        setBtn = gui.Button("Med. Gear PID")
        pidFrame.append(setBtn)

        def setPids(widget):
            drivetrain.mediumPositionGear.p = float(pIn.get_value())
            drivetrain.mediumPositionGear.i = float(iIn.get_value())
            drivetrain.mediumPositionGear.d = float(dIn.get_value())
            drivetrain.mediumPositionGear.f = float(fIn.get_value())
        setBtn.onclick.connect(setPids)

        return testBox

    def updateRobotPosition(self, robotX, robotY, robotAngle):
        self.robotArrow.setPosition(robotX, robotY, robotAngle)
        self.robotPositionLbl.set_text('%.3f, %.3f, %.3f' %
            (robotX, robotY, math.degrees(robotAngle)))

    def updateCursorPosition(self):
        coord = self.selectedCoord
        self.cursorArrow.setPosition(
            coord.x, coord.y, coord.orientation)
        self.cursorPositionLbl.set_text('%.3f, %.3f, %.3f' %
            (coord.x, coord.y, math.degrees(coord.orientation)))

    def updateScheduler(self):
        scheduler = self.robot.autoScheduler
        self.schedulerList.empty()

        for line in self.robotPathLines:
            self.fieldSvg.remove_child(line)
        self.robotPathLines.clear()
        lineX, lineY = fieldToSvgCoordinates(self.robotArrow.x, self.robotArrow.y)

        index = 0
        for action in scheduler.actionList:
            name = action.name
            if action == scheduler.runningAction:
                name = "* " + name
            listItem = gui.ListItem(name)
            self.schedulerList.append(listItem, str(index))
            lineX, lineY = self.actionLines(lineX, lineY, action)
            index += 1

    def actionLines(self, lineX, lineY, action):
        for coord in action.coords:
            x1, y1 = fieldToSvgCoordinates(coord[0], coord[1])
            line = gui.SvgLine(lineX, lineY, x1, y1)
            line.set_stroke(width=3)
            self.robotPathLines.append(line)
            self.fieldSvg.append(line)
            lineX, lineY = x1, y1
        return lineX, lineY

    # WIDGET CALLBACKS

    def c_closeApp(self, button):
        self.close()

    def c_setRobotPosition(self, button):
        coord = self.selectedCoord
        self.robot.pathFollower.setPosition(
            coord.x, coord.y, coord.orientation)

    def c_addGenericAction(self, listview, key):
        speed = float(self.speedInput.get_value())
        if key == "drivetopoint":
            action = auto_actions.createDriveToPointAction(
                self.robot.pathFollower, self.selectedCoord, speed)
        elif key == "navigatetopoint":
            action = auto_actions.createNavigateToPointAction(
                self.robot.pathFollower, self.selectedCoord, speed)
        elif key == "setposition":
            action = auto_actions.createSetRobotPositionAction(
                self.robot.pathFollower, self.selectedCoord)
        else:
            action = self.robot.genericAutoActions[int(key)]
        self.robot.autoScheduler.actionList.append(action)
        self.updateScheduler()

    def c_clearSchedule(self, button):
        self.robot.autoScheduler.actionList.clear()
        self.updateScheduler()

    def c_removeAction(self, listview, key):
        index = int(key)
        actionList = self.robot.autoScheduler.actionList
        if index < len(actionList):
            del actionList[index]
        self.updateScheduler()
