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

        root = gui.VBox(width=1000, margin='0px auto')

        sideHBox = gui.HBox()
        sideHBox.style['align-items'] = 'flex-start' # both panels align to top
        root.append(sideHBox)
        leftSide = gui.VBox()
        leftSide.style['align-items'] = 'stretch'
        sideHBox.append(leftSide)
        rightSide = gui.VBox()
        rightSide.style['align-items'] = 'flex-start'
        sideHBox.append(rightSide)

        rightSide.append(self.initCamera())

        testFrame = self.initTestControl(robot)

        rightSide.append(self.initFieldMap(robot))
        self.selectedCoord = coordinates.DriveCoordinate("Center", 0, 0, math.radians(-90))
        self.updateCursorPosition()

        rightSide.append(testFrame)

        hbox1 = gui.HBox()
        hbox1.style['align-items'] = 'stretch'
        leftSide.append(hbox1)
        hbox1.append(self.initGeneral(robot))
        hbox1.append(self.initWheelControls(robot))

        leftSide.append(self.initManualControls(robot))

        leftSide.append(self.initScheduler(robot))
        self.updateScheduler()
        self.updateSchedulerFlag = False

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

    def initCamera(self):
        cameraBox = self.sectionBox()
        cameraBox.set_size(640, 240)

        videoChoiceBox = gui.HBox(gui.Label('Video Feeds'))
        cameraBox.append(videoChoiceBox)

        for camera in ['Limelight','Camera 2','Camera 3']:
            button = gui.Button(camera)
            button.onclick.connect(self.c_switchVideoFeed)
            videoChoiceBox.append(button)
        self.videoFeed = gui.Image('http://10.26.5.6:5800/')

        cameraBox.append(self.videoFeed)

        return cameraBox

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

        self.realTimeRatioLbl = gui.Label("1.000")
        generalBox.append(sea.hBoxWith(gui.Label("Slowdown:"),
            self.spaceBox(), self.realTimeRatioLbl))

        return generalBox

    def initManualControls(self, robot):
        manualBox = self.sectionBox()
        manualBox.append(gui.Label("MANUAL"))

        auxModeBox = gui.HBox()
        manualBox.append(auxModeBox)
        self.auxModeGroup = sea.ToggleButtonGroup()

        defenseButton = gui.Button("Defense")
        defenseButton.onclick.connect(robot.c_defenseMode)
        self.auxModeGroup.addButton(defenseButton, "defense")
        auxModeBox.append(defenseButton)

        cargoButton = gui.Button("Cargo")
        cargoButton.onclick.connect(robot.c_cargoMode)
        self.auxModeGroup.addButton(cargoButton, "cargo")
        auxModeBox.append(cargoButton)
        
        hatchButton = gui.Button("Hatch")
        hatchButton.onclick.connect(robot.c_hatchMode)
        self.auxModeGroup.addButton(hatchButton, "hatch")
        auxModeBox.append(hatchButton)

        climbBtn = gui.Button("Climb")
        climbBtn.onclick.connect(robot.c_climbMode)
        self.auxModeGroup.addButton(climbBtn, "climb")
        auxModeBox.append(climbBtn)

        speedBox = gui.HBox()
        manualBox.append(speedBox)
        
        slowBtn = gui.Button("Slow")
        slowBtn.onclick.connect(robot.c_slowGear)
        speedBox.append(slowBtn)
        mediumBtn = gui.Button("Medium")
        mediumBtn.onclick.connect(robot.c_mediumGear)
        speedBox.append(mediumBtn)
        fastBtn = gui.Button("Fast")
        fastBtn.onclick.connect(robot.c_fastGear)
        speedBox.append(fastBtn)

        self.gearGroup = sea.ToggleButtonGroup()
        self.gearGroup.addButton(slowBtn, "slow")
        self.gearGroup.addButton(mediumBtn, "medium")
        self.gearGroup.addButton(fastBtn, "fast")

        toggleBox = gui.HBox()
        manualBox.append(toggleBox)

        voltageToggle = gui.Button("Drive Voltage")
        voltageToggle.onclick.connect(robot.c_toggleVoltage)
        toggleBox.append(voltageToggle)
        self.voltageModeGroup = sea.ToggleButtonGroup()
        self.voltageModeGroup.addButton(voltageToggle, True)
        self.voltageModeGroup.highlight(robot.driveVoltage)

        fieldOrientedToggle = gui.Button("Field Oriented")
        fieldOrientedToggle.onclick.connect(robot.c_toggleFieldOriented)
        toggleBox.append(fieldOrientedToggle)
        self.fieldOrientedGroup = sea.ToggleButtonGroup()
        self.fieldOrientedGroup.addButton(fieldOrientedToggle, True)
        self.fieldOrientedGroup.highlight(robot.fieldOriented)

        return manualBox

    def initWheelControls(self, robot):
        wheelControlsBox = self.sectionBox()

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

        robotBox = gui.HBox()
        fieldBox.append(robotBox)

        setPositionBtn = gui.Button("Set Robot to Cursor")
        setPositionBtn.onclick.connect(self.c_setRobotPosition)
        robotBox.append(setPositionBtn)

        def setRobotAngle(button, angle):
            pathFollower = self.robot.pathFollower
            pathFollower.setPosition(pathFollower.robotX, pathFollower.robotY, angle)
        leftBtn = gui.Button('<')
        leftBtn.onclick.connect(setRobotAngle, math.radians(90))
        robotBox.append(leftBtn)
        rightBtn = gui.Button('>')
        rightBtn.onclick.connect(setRobotAngle, math.radians(-90))
        robotBox.append(rightBtn)
        upBtn = gui.Button('^')
        upBtn.onclick.connect(setRobotAngle, 0)
        robotBox.append(upBtn)
        downBtn = gui.Button('v')
        downBtn.onclick.connect(setRobotAngle, math.radians(180))
        robotBox.append(downBtn)

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

        self.controlModeGroup = sea.ToggleButtonGroup()
        self.controlModeGroup.addButton(manualModeBtn, "manual")
        self.controlModeGroup.addButton(autoModeBtn, "auto")

        hbox = gui.HBox()
        hbox.style['align-items'] = 'flex-start'
        schedulerBox.append(hbox)

        addActionBox = gui.VBox()
        hbox.append(addActionBox)

        self.autoSpeed = 6
        def slowSpeed():
            self.autoSpeed = 3
        def mediumSpeed():
            self.autoSpeed = 6
        def fastSpeed():
            self.autoSpeed = 10

        speedTabBox = gui.TabBox()
        speedTabBox.add_tab(gui.Widget(), "Slow", slowSpeed)
        speedTabBox.add_tab(gui.Widget(), "Med", mediumSpeed)
        speedTabBox.add_tab(gui.Widget(), "Fast", fastSpeed)
        speedTabBox.select_by_index(1)
        addActionBox.append(speedTabBox)

        addActionBox.append(gui.Label("Auto actions:"))

        genericActionList = gui.ListView()
        genericActionList.append("Drive to Point", "drivetopoint")
        genericActionList.append("Navigate to Point", "navigatetopoint")
        index = 0
        for action in robot.genericAutoActions:
            genericActionList.append(gui.ListItem(action.name), str(index))
            index += 1
        genericActionList.onselection.connect(self.c_addGenericAction)
        addActionBox.append(genericActionList)

        hbox.append(self.spaceBox())

        scheduleListBox = gui.VBox()
        hbox.append(scheduleListBox)
        clearScheduleBox = gui.HBox()
        clearScheduleBox.style['align-items'] = 'flex-end'
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

        swerveBrakeBox = gui.HBox()
        testBox.append(swerveBrakeBox)

        swerveBrakeOffBtn = gui.Button("Swerve Brake Off")
        swerveBrakeOffBtn.onclick.connect(robot.c_swerveBrakeOff)
        swerveBrakeBox.append(swerveBrakeOffBtn)

        swerveBrakeOnBtn = gui.Button("Swerve Brake On")
        swerveBrakeOnBtn.onclick.connect(robot.c_swerveBrakeOn)
        swerveBrakeBox.append(swerveBrakeOnBtn)
        


        resetClawBtn = gui.Button("Reset Claw")
        resetClawBtn.onclick.connect(robot.c_resetClaw)
        testBox.append(resetClawBtn)

<<<<<<< HEAD
        posBox = gui.HBox()
        testBox.append(posBox)

        posBox.append(gui.Label("Robot:"))
        posBox.append(self.spaceBox())
        self.robotPositionLbl = gui.Label('')
        posBox.append(self.robotPositionLbl)
        posBox.append(self.spaceBox())

        cursorBox = gui.HBox()
        testBox.append(cursorBox)

        cursorBox.append(gui.Label("Cursor:"))
        cursorBox.append(self.spaceBox())
        self.cursorPositionLbl = gui.Label('')
        cursorBox.append(self.cursorPositionLbl)
        cursorBox.append(self.spaceBox())
=======
>>>>>>> 8b6499a5e4583117a5a89731e2b60acb790da44c
        xInput = gui.Input()
        yInput = gui.Input()
        angleInput = gui.Input()
        smallBox = sea.vBoxWith(xInput,yInput)
        cursorToPtBtn = gui.Button('Move Cursor to Point')
        cursorToPtBtn.set_on_click_listener(self.moveCursortoPt,xInput,yInput,angleInput)
        testBox.append(sea.hBoxWith(smallBox,angleInput,cursorToPtBtn))

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
    
    def moveCursortoPt(self,widget,xInput,yInput,angleInput):
        try:
            x = int(xInput.get_value())
            y = int(yInput.get_value())
        except ValueError:
            x = self.selectedCoord.x
            y = self.selectedCoord.y
        angle = math.radians(float(angleInput.get_value()))
        self.selectedCoord = coordinates.DriveCoordinate("Selected",
            x,y,angle)
        self.updateCursorPosition()

    # WIDGET CALLBACKS

    def c_closeApp(self, button):
        self.close()

    def c_setRobotPosition(self, button):
        coord = self.selectedCoord
        self.robot.pathFollower.setPosition(
            coord.x, coord.y, coord.orientation)

    def c_addGenericAction(self, listview, key):
        if key == "drivetopoint":
            action = auto_actions.createDriveToPointAction(
                self.robot.pathFollower, self.robot.vision,
                self.selectedCoord, self.autoSpeed)
        elif key == "navigatetopoint":
            action = auto_actions.createNavigateToPointAction(
                self.robot.pathFollower, self.robot.vision,
                self.selectedCoord, self.autoSpeed)
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

    def c_switchVideoFeed(self,button):
        if button.get_text() == 'Limelight':
            print('Switch feed to Limelight')
            self.videoFeed.set_image('http://10.26.5.6:5800/')
        elif button.get_text() == 'Camera 2':
            print('Switch feed to Camera 2')
            self.videoFeed.set_image('https://avatars2.githubusercontent.com/u/13607012?s=280&v=4')
        else:
            print('Switch feed to Camera 3')
