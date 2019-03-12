import math
import remi.gui as gui
import seamonsters as sea
import coordinates
import drivetrain
import auto_actions
import random
import json
import os
import glob

CROSSHAIR_X = 320
CROSSHAIR_Y = 120
CROSSHAIR_SIZE = 100
CROSSHAIR_WIDTH = 4

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

    def __init__(self, num, wheel, robot, isSwerve):
        self.wheel = wheel
        self.name = chr(ord('A') + num)
        if isSwerve:
            self.name += 's'
        else:
            self.name += 'd'
        self.button = gui.Button(self.name)
        self._buttonColor("green")
        self.button.controller = self
        self.button.onclick.connect(robot.c_wheelButtonClicked)

    def _buttonColor(self, color):
        self.button.style["background"] = color

    def update(self):
        if self.wheel.disabled:
            self.wheel.faults.clear()
            return
        while len(self.wheel.faults) > 0:
            print("Wheel", self.name, "fault:", self.wheel.faults.pop(0))
            self._buttonColor("red")

    def reset(self):
        if not self.wheel.disabled:
            self._buttonColor("green")

    def clicked(self):
        if not self.wheel.disabled:
            self.wheel.disabled = True
            self._buttonColor("black")
        else:
            self.wheel.disabled = False
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

    def presetPath(self):
        return sea.getRobotPath('auto_sequence_presets')

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
        self.fpsLbl.set_text(
            '%d FPS' % (self.robot.timingMonitor.fps,))
        for wheelButton in self.wheelBtns:
            wheelButton.update()

        if self.updateSchedulerFlag:
            self.updateScheduler()
            self.updateSchedulerFlag = False

    def initCamera(self):
        cameraBox = self.sectionBox()

        videoChoiceBox = gui.HBox(gui.Label('Video Feeds'))
        cameraBox.append(videoChoiceBox)

        for camera in ['Limelight','Camera 2','Camera 3']:
            button = gui.Button(camera)
            button.onclick.connect(self.c_switchVideoFeed)
            videoChoiceBox.append(button)

        staticBox = gui.Widget()
        staticBox.set_size(640, 240)
        cameraBox.append(staticBox)
        relativeBox = gui.Widget()
        relativeBox.style["position"] = "relative"
        relativeBox.style["top"] = "0px"
        relativeBox.style["left"] = "0px"
        staticBox.append(relativeBox)

        self.videoFeed = gui.Image('http://10.26.5.6:5800/')
        self.videoFeed.style["top"] = "0px"
        self.videoFeed.style["left"] = "0px"
        self.videoFeed.style["position"] = "absolute"
        self.videoFeed.style["z-index"] = "1"
        relativeBox.append(self.videoFeed)
        self.setVideoFeed(0)

        horizLine = gui.Widget()
        horizLine.set_size(CROSSHAIR_SIZE, CROSSHAIR_WIDTH)
        horizLine.style["background"] = "#66FF00"
        horizLine.style["left"] = str(CROSSHAIR_X - CROSSHAIR_SIZE/2) + "px"
        horizLine.style["top"] = str(CROSSHAIR_Y - CROSSHAIR_WIDTH/2) + "px"
        horizLine.style["position"] = "absolute"
        horizLine.style["z-index"] = "2"
        relativeBox.append(horizLine)

        vertLine = gui.Widget()
        vertLine.set_size(CROSSHAIR_WIDTH, CROSSHAIR_SIZE)
        vertLine.style["background"] = "#66FF00"
        vertLine.style["left"] = str(CROSSHAIR_X - CROSSHAIR_WIDTH/2) + "px"
        vertLine.style["top"] = str(CROSSHAIR_Y - CROSSHAIR_SIZE/2) + "px"
        vertLine.style["position"] = "absolute"
        vertLine.style["z-index"] = "2"
        relativeBox.append(vertLine)

        return cameraBox

    def initGeneral(self, robot):
        generalBox = self.sectionBox()

        closeButton = gui.Button("Close")
        closeButton.onclick.connect(self.c_closeApp)
        generalBox.append(closeButton)

        connectionTestButton = gui.Button("Connection Test")
        generalBox.append(connectionTestButton)
        def connectionTest(button):
            color = "rgb(%d, %d, %d)" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            connectionTestButton.style["background"] = color
        connectionTestButton.onclick.connect(connectionTest)

        self.fpsLbl = gui.Label("FPS")
        generalBox.append(self.fpsLbl)

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

        def resetWheelButtons(widget):
            for controller in self.wheelBtns:
                controller.reset()

        resetBtn = gui.Button("Reset")
        resetBtn.onclick.connect(resetWheelButtons)
        wheelControlsBox.append(resetBtn)

        grid = gui.GridBox()
        grid.define_grid([['Cd','Dd','space1','Cs','Ds'],
                          ['Ad','Bd','space1','As','Bs']])
        wheelControlsBox.append(grid)

        self.wheelBtns = []
        def addButton(b):
            grid.append(b.button, b.name)
            self.wheelBtns.append(b)
        for wheelIndex in range(4):
            addButton(WheelButtonController(wheelIndex,
                robot.superDrive.wheels[wheelIndex].angledWheel, robot, False))
            addButton(WheelButtonController(wheelIndex,
                robot.superDrive.wheels[wheelIndex], robot, True))
        grid.append(self.spaceBox(), 'space1')
        grid.append(self.spaceBox(), 'space2')

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
            self.autoSpeed = 8

        speedTabBox = gui.TabBox()
        speedTabBox.add_tab(gui.Widget(), "Slow", slowSpeed)
        speedTabBox.add_tab(gui.Widget(), "Med", mediumSpeed)
        speedTabBox.add_tab(gui.Widget(), "Fast", fastSpeed)
        speedTabBox.select_by_index(1)
        addActionBox.append(speedTabBox)

        addActionBox.append(gui.Label("Auto actions:"))

        self.genericActionList = gui.ListView()
        self.genericActionList.append("Drive to Point", "drivetopoint")
        self.genericActionList.append("Navigate to Point", "navigatetopoint")
        self.genericActionList.append("Rotate in place", "rotate")
        index = 0
        for action in robot.genericAutoActions:
            self.genericActionList.append(gui.ListItem(action.name), str(index))
            index += 1
        self.genericActionList.onselection.connect(self.c_addGenericAction)
        addActionBox.append(self.genericActionList)

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
        
        schedulePresetLbl = gui.Label("Auto Schedule Presets")
        schedulerBox.append(schedulePresetLbl)
        schedulePresets = gui.HBox()
        schedulerBox.append(schedulePresets)
        self.presetDropdown = gui.DropDown()
        self.updatePresetFileDropdown()
        schedulerBox.append(self.presetDropdown)
        presetIn = gui.Input(default_value="file name")
        schedulePresets.append(presetIn)
        openPresetBtn = gui.Button("Open")
        schedulePresets.append(openPresetBtn)
        openPresetBtn.onclick.connect(self.c_openAutoPreset, self.presetDropdown)
        newPresetBtn = gui.Button("New")
        schedulePresets.append(newPresetBtn)
        newPresetBtn.onclick.connect(self.c_saveAutoPresetFromText, presetIn)
        schedulePresets.append(newPresetBtn)
        savePresetBtn = gui.Button("Save")
        schedulePresets.append(savePresetBtn)
        savePresetBtn.onclick.connect(self.c_saveAutoPresetFromDropdown, self.presetDropdown)
        schedulePresets.append(savePresetBtn)
        deletePresetBtn = gui.Button("Delete")
        schedulePresets.append(deletePresetBtn)
        deletePresetBtn.onclick.connect(self.c_deleteAutoPreset, self.presetDropdown)
        schedulePresets.append(deletePresetBtn)

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
            angle = math.radians(float(angleInput.get_value()))
        except ValueError:
            return
        self.selectedCoord = coordinates.DriveCoordinate("Entered",
            x,y,angle)
        self.updateCursorPosition()

    def setVideoFeed(self, num):
        self.cameraNum = num
        if num == 0:
            print('Switch feed to Limelight')
            self.videoFeed.set_image('http://10.26.5.6:5800/')
        elif num == 1:
            print('Switch feed to Camera 2')
            self.videoFeed.set_image('http://10.26.5.2:5806/stream.mjpg')
        elif num == 2:
            print('Switch feed to Camera 3')
            self.videoFeed.set_image('http://10.26.5.2:5807/stream.mjpg')

    def toggleVideoFeed(self):
        self.setVideoFeed((self.cameraNum + 1) % 2)

    def updatePresetFileDropdown(self):
        self.presetDropdown.empty()
        for file in glob.glob(os.path.join(self.presetPath(), "*.json")):
            fileName = os.path.basename(file)
            self.presetDropdown.append(fileName, file)

    def saveAutoPreset(self, fileLocation):
        autoPreset = self.robot.autoScheduler.toJson()
        with open(fileLocation,"w") as presetFile:
            json.dump(autoPreset, presetFile)
        print("Preset saved")
        self.updatePresetFileDropdown()

    # WIDGET CALLBACKS

    def c_closeApp(self, button):
        self.close()

    def c_openAutoPreset(self, dropDownItem, file):
        if file.get_key() is None:
            print("No file selected")
            return
        #file should be blank because it will delete everything in it otherwise
        self.robot.autoScheduler.actionList.clear()
        with open(file.get_key(),"r") as presetFile:
            preset = json.load(presetFile)
            for action in preset:
                if action["coord"] != []:
                    self.c_addGenericAction(self.genericActionList, action["key"], \
                        coordinates.DriveCoordinate(action["coord"][0], action["coord"][1], action["coord"][2], \
                            action["coord"][3], action["coord"][4]))
                else:
                    self.c_addGenericAction(self.genericActionList, action["key"], None)
        self.updatePresetFileDropdown()

    def c_saveAutoPresetFromText(self, button, textInput):
        #file needs to be blank 
        self.saveAutoPreset(os.path.join(self.presetPath(), textInput.get_value() + ".json"))

    def c_saveAutoPresetFromDropdown(self, dropDownItem, file):
        #file needs to be blank
        if file.get_key() is None:
            print("No file selected")
            return
        self.saveAutoPreset(file.get_key())

    def c_deleteAutoPreset(self, dropDownItem, file):
        if file.get_key() is None:
            print("No file selected")
            return
        os.unlink(file.get_key())
        self.updatePresetFileDropdown()
        
    def c_setRobotPosition(self, button):
        coord = self.selectedCoord
        self.robot.pathFollower.setPosition(
            coord.x, coord.y, coord.orientation)

    def c_addGenericAction(self, listview, key, driveCoordinate=None):
        if driveCoordinate is None:
            driveCoordinate = self.selectedCoord
        if key == "drivetopoint":
            action = auto_actions.createDriveToPointAction(
                self.robot.pathFollower, self.robot.vision,
                driveCoordinate, self.autoSpeed, key)
        elif key == "navigatetopoint":
            action = auto_actions.createNavigateToPointAction(
                self.robot.pathFollower, self.robot.vision,
                driveCoordinate, self.autoSpeed, key)
        elif key == "rotate":
            action = auto_actions.createRotateInPlaceAction(
                self.robot.pathFollower, driveCoordinate, key)
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
            self.setVideoFeed(0)
        elif button.get_text() == 'Camera 2':
            self.setVideoFeed(1)
        else:
            self.setVideoFeed(2)
