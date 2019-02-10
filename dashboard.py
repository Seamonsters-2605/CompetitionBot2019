import math
import remi.gui as gui
import seamonsters as sea
import coordinates
import drivetrain

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

        clawModeBox = gui.HBox()
        root.append(clawModeBox)

        defenseButton = gui.Button("Defense Mode")
        defenseButton.onclick.connect(robot.c_defenseMode)
        clawModeBox.append(defenseButton)

        cargoButton = gui.Button("Cargo Mode")
        cargoButton.onclick.connect(robot.c_cargoMode)
        clawModeBox.append(cargoButton)
        
        hatchButton = gui.Button("Hatch Mode")
        hatchButton.onclick.connect(robot.c_hatchMode)
        clawModeBox.append(hatchButton)
        
        self.realTimeRatioLbl = gui.Label("[real time ratio]")
        root.append(self.realTimeRatioLbl)

        self.currentLbl = gui.Label("[current]")
        root.append(self.currentLbl)

        compressorBox = gui.HBox()
        root.append(compressorBox)
        compressorBox.append(gui.Label("Compressor:"))
        startCompressorBtn = gui.Button("Start")
        startCompressorBtn.onclick.connect(robot.c_startCompressor)
        compressorBox.append(startCompressorBtn)
        stopCompressorBtn = gui.Button("Stop")
        stopCompressorBtn.onclick.connect(robot.c_stopCompressor)
        compressorBox.append(stopCompressorBtn)

        zeroSteeringBtn = gui.Button("Reset swerve rotations")
        zeroSteeringBtn.onclick.connect(robot.c_wheelsToZero)
        root.append(zeroSteeringBtn)

        self.fieldOrientedLbl = gui.Label("[field oriented state]")
        root.append(self.fieldOrientedLbl)

        root.append(self.initGearSelector(robot))

        self.encoderLbl = gui.Label("[encoder values]")
        root.append(self.encoderLbl)

        root.append(self.initWheelControlls(robot))

        root.append(self.initFieldMap(robot))
        self.selectedCoord = coordinates.DriveCoordinate("Center", 0, 0, 0)
        self.updateCursorPosition()

        root.append(self.initScheduler(robot))
        self.updateScheduler()

        appCallback(self)
        return root

    def idle(self):
        pf = self.robot.pathFollower
        self.updateRobotPosition(
            pf.robotX, pf.robotY, pf.robotAngle)
        self.realTimeRatioLbl.set_text(
            '%.3f' % (self.robot.timingMonitor.realTimeRatio,))
        self.currentLbl.set_text(self.robot.lbl_current)
        self.encoderLbl.set_text(self.robot.lbl_encoder)
        self.updateBrokenEncoderButton(self.robot)

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

        pidFrame = gui.HBox()
        gearSelectorBox.append(pidFrame)
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
        setBtn = gui.Button("PID")
        pidFrame.append(setBtn)

        def setPids(widget):
            drivetrain.mediumPositionGear.p = float(pIn.get_value())
            drivetrain.mediumPositionGear.i = float(iIn.get_value())
            drivetrain.mediumPositionGear.d = float(dIn.get_value())
            drivetrain.mediumPositionGear.f = float(fIn.get_value())
            print("PIDS", drivetrain.mediumPositionGear)
        setBtn.onclick.connect(setPids)

        return gearSelectorBox

    def initWheelControlls(self, robot):
        wheelControllsBox = gui.VBox()
        self.groupStyle(wheelControllsBox)

        self.wheelControllsLbl = gui.Label("[wheel controlls]")
        wheelControllsBox.append(self.wheelControllsLbl)
        self.wheelBtns = [None] * 4
        
        wheelsBox = gui.HBox()
        wheelControllsBox.append(wheelsBox)
        for wheelIndex in range(4):
            newButton = gui.Button(str(wheelIndex + 1))
            newButton.wheelNum = wheelIndex + 1
            newButton.onclick.connect(robot.c_disableWheel)
            self.wheelBtns[wheelIndex] = newButton
            wheelsBox.append(newButton)

        return wheelControllsBox

    def initFieldMap(self, robot):
        fieldBox = gui.VBox()
        self.groupStyle(fieldBox)

        posBox = gui.HBox()
        fieldBox.append(posBox)

        self.target_points = coordinates.targetPoints

        self.robotPositionLbl = gui.Label("[robot position]")
        posBox.append(self.robotPositionLbl)

        resetPositionBtn = gui.Button("Reset position")
        resetPositionBtn.onclick.connect(robot.c_resetPosition)
        posBox.append(resetPositionBtn)

        cursorBox = gui.HBox()
        fieldBox.append(cursorBox)
        self.cursorXInput = gui.Input()
        self.cursorXInput.set_value("0")
        cursorBox.append(self.cursorXInput)
        self.cursorYInput = gui.Input()
        self.cursorYInput.set_value("0")
        cursorBox.append(self.cursorYInput)
        self.cursorAngleInput = gui.Input()
        self.cursorAngleInput.set_value("0")
        cursorBox.append(self.cursorAngleInput)
        setCursorBtn = gui.Button("Set cursor")
        cursorBox.append(setCursorBtn)

        def setCursor(button):
            self.selectedCoord = coordinates.DriveCoordinate("Entered",
                float(self.cursorXInput.get_value()),
                float(self.cursorYInput.get_value()),
                math.radians(float(self.cursorAngleInput.get_value())))
            self.updateCursorPosition()
        setCursorBtn.onclick.connect(setCursor)

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

        for point in self.target_points:
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
        for point in self.target_points:
            if math.hypot(x - point.x, y - point.y) < 1:
                self.selectedCoord = point
        self.updateCursorPosition()
        self.cursorXInput.set_value(str(self.selectedCoord.x))
        self.cursorYInput.set_value(str(self.selectedCoord.y))
        self.cursorAngleInput.set_value(str(math.degrees(self.selectedCoord.orientation)))
        print(x,y)

    def initScheduler(self, robot):
        schedulerBox = gui.VBox()
        self.groupStyle(schedulerBox)

        addActionBox = gui.VBox()
        addActionBox.append(gui.Label("Add Action:"))
        schedulerBox.append(addActionBox)

        # BEGIN ADD ACTION BUTTONS

        speedBox = gui.HBox()
        addActionBox.append(speedBox)
        speedBox.append(gui.Label("Speed:"))
        self.speedInput = gui.Input()
        self.speedInput.set_value("5")
        speedBox.append(self.speedInput)

        driveToPointActionBox = gui.HBox()
        addActionBox.append(driveToPointActionBox)
        addDriveToPointActionBtn = gui.Button('Drive to Point')
        addDriveToPointActionBtn.onclick.connect(robot.c_addDriveToPointAction)
        driveToPointActionBox.append(addDriveToPointActionBtn)
        addNavigateActionBtn = gui.Button('Navigate to Point')
        addNavigateActionBtn.onclick.connect(robot.c_addNavigateAction)
        driveToPointActionBox.append(addNavigateActionBtn)

        addVisionAlignActionBtn = gui.Button('Vision Align')
        addVisionAlignActionBtn.onclick.connect(robot.c_addVisionAlignAction)
        addActionBox.append(addVisionAlignActionBtn)

        # END ADD ACTION BUTTONS

        controlBox = gui.HBox()
        schedulerBox.append(controlBox)

        pauseResumeButton = gui.Button('Start')
        pauseResumeButton.onclick.connect(robot.c_toggleAutoScheduler)
        controlBox.append(pauseResumeButton)
        clearAllButton = gui.Button("Clear All")
        clearAllButton.onclick.connect(robot.c_clearAll)
        controlBox.append(clearAllButton)
        cancelCurrentActionBtn = gui.Button("Cancel Current Action")
        cancelCurrentActionBtn.onclick.connect(robot.c_cancelRunningAction)
        controlBox.append(cancelCurrentActionBtn)

        schedulerBox.append(gui.Label("Schedule:"))

        self.schedulerList = gui.ListView()
        schedulerBox.append(self.schedulerList)

        return schedulerBox

    def updateRobotPosition(self, robotX, robotY, robotAngle):
        self.robotArrow.setPosition(robotX, robotY, robotAngle)
        self.robotPositionLbl.set_text('%.3f, %.3f, %.3f' %
            (robotX, robotY, math.degrees(robotAngle)))

    def updateCursorPosition(self):
        self.cursorArrow.setPosition(
            self.selectedCoord.x, self.selectedCoord.y, self.selectedCoord.orientation)

    def updateScheduler(self):
        scheduler = self.robot.autoScheduler
        self.schedulerList.empty()

        for line in self.robotPathLines:
            self.fieldSvg.remove_child(line)
        self.robotPathLines.clear()
        lineX, lineY = fieldToSvgCoordinates(self.robotArrow.x, self.robotArrow.y)

        if scheduler.runningAction is not None:
            runningItem = gui.ListItem('* ' + scheduler.runningAction.name)
            self.schedulerList.append(runningItem)
            lineX, lineY = self.actionLines(lineX, lineY, scheduler.runningAction)
        for action in scheduler.actionList:
            listItem = gui.ListItem(action.name)
            self.schedulerList.append(listItem)
            lineX, lineY = self.actionLines(lineX, lineY, action)

    def actionLines(self, lineX, lineY, action):
        for coord in action.coords:
            x1, y1 = fieldToSvgCoordinates(coord[0], coord[1])
            line = gui.SvgLine(lineX, lineY, x1, y1)
            line.set_stroke(width=3)
            self.robotPathLines.append(line)
            self.fieldSvg.append(line)
            lineX, lineY = x1, y1
        return lineX, lineY

    def switchDeadWheelText(self, button):
        if button.get_text() != "dead":
            button.set_text("dead")
        else:
            button.set_text(str(button.wheelNum))
            
    #if the encoder stops working, the button attached to it turns red
    def updateBrokenEncoderButton(self, robot):
        for button in self.wheelBtns:
            if not robot.superDrive.wheels[button.wheelNum - 1].angledWheel.encoderWorking:
                button.style["background"] = "red"

    def toggleAutoScheduler(self, button):
        if button.get_text() == "Pause":
            button.set_text("Resume")
        else:
            button.set_text("Pause")

    def c_closeApp(self, button):
        self.close()