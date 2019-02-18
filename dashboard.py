import math
import remi.gui as gui
import seamonsters as sea
import coordinates
import drivetrain
import auto_actions

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

    def spaceBox(self):
        return gui.HBox(width=10)

    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.VBox(width=600, margin='0px auto')

        closeButton = gui.Button("Close")
        closeButton.onclick.connect(self.c_closeApp)
        root.append(closeButton)

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

        root.append(self.initManualControls(robot))

        self.encoderLbl = gui.Label("[encoder values]")
        root.append(self.encoderLbl)

        root.append(self.initWheelControlls(robot))

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
        self.currentLbl.set_text(self.robot.lbl_current)
        self.encoderLbl.set_text(self.robot.lbl_encoder)
        self.updateBrokenEncoderButton(self.robot)

        if self.updateSchedulerFlag:
            self.updateScheduler()
            self.updateSchedulerFlag = False

    def initManualControls(self, robot):
        manualBox = gui.VBox()
        self.groupStyle(manualBox)
        manualBox.append(gui.Label("MANUAL"))

        clawModeBox = gui.HBox()
        manualBox.append(clawModeBox)

        defenseButton = gui.Button("Defense Mode")
        defenseButton.onclick.connect(robot.c_defenseMode)
        clawModeBox.append(defenseButton)

        cargoButton = gui.Button("Cargo Mode")
        cargoButton.onclick.connect(robot.c_cargoMode)
        clawModeBox.append(cargoButton)
        
        hatchButton = gui.Button("Hatch Mode")
        hatchButton.onclick.connect(robot.c_hatchMode)
        clawModeBox.append(hatchButton)

        self.fieldOrientedLbl = gui.Label("[field oriented state]")
        manualBox.append(self.fieldOrientedLbl)

        self.driveGearLbl = gui.Label("[drive gear]")
        manualBox.append(self.driveGearLbl)

        voltageModeBox = gui.HBox()
        manualBox.append(voltageModeBox)
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
        manualBox.append(velocityModeBox)
        slowVelocityBtn = gui.Button("Slow Position")
        slowVelocityBtn.onclick.connect(robot.c_slowPositionGear)
        velocityModeBox.append(slowVelocityBtn)
        mediumVelocityBtn = gui.Button("Medium Position")
        mediumVelocityBtn.onclick.connect(robot.c_mediumPositionGear)
        velocityModeBox.append(mediumVelocityBtn)
        fastVelocityBtn = gui.Button("Fast Position")
        fastVelocityBtn.onclick.connect(robot.c_fastPositionGear)
        velocityModeBox.append(fastVelocityBtn)

        elevatorBox = gui.HBox()
        manualBox.append(elevatorBox)

        elevatorFreeBtn = gui.Button("Elevator Free")
        elevatorFreeBtn.onclick.connect(robot.c_elevatorFree)
        elevatorBox.append(elevatorFreeBtn)
        elevatorGBtn = gui.Button("G")
        elevatorGBtn.onclick.connect(robot.c_elevatorG)
        elevatorBox.append(elevatorGBtn)
        elevator1Btn = gui.Button("1")
        elevator1Btn.onclick.connect(robot.c_elevator1)
        elevatorBox.append(elevator1Btn)
        elevator2Btn = gui.Button("2")
        elevator2Btn.onclick.connect(robot.c_elevator2)
        elevatorBox.append(elevator2Btn)
        elevator3Btn = gui.Button("3")
        elevator3Btn.onclick.connect(robot.c_elevator3)
        elevatorBox.append(elevator3Btn)

        climberBox = gui.HBox()
        manualBox.append(climberBox)

        climberRevBtn = gui.Button("Climber REV")
        climberRevBtn.onmousedown.connect(robot.c_climberRev)
        climberRevBtn.onmouseup.connect(robot.c_climberStop)
        climberBox.append(climberRevBtn)
        climberStopBtn = gui.Button("Climber STOP")
        climberStopBtn.onclick.connect(robot.c_climberStop)
        climberBox.append(climberStopBtn)
        climberFwdBtn = gui.Button("Climber FWD")
        climberFwdBtn.onmousedown.connect(robot.c_climberFwd)
        climberFwdBtn.onmouseup.connect(robot.c_climberStop)
        climberBox.append(climberFwdBtn)

        return manualBox

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

        navigationBox = gui.HBox()
        addActionBox.append(navigationBox)
        actionDriveToPointBtn = gui.Button('Drive to Point')
        actionDriveToPointBtn.onclick.connect(self.c_actionDriveToPoint)
        navigationBox.append(actionDriveToPointBtn)
        actionNavigateBtn = gui.Button('Navigate to Point')
        actionNavigateBtn.onclick.connect(self.c_actionNavigate)
        navigationBox.append(actionNavigateBtn)

        actionVisionAlignBtn = gui.Button('Vision Align')
        actionVisionAlignBtn.onclick.connect(self.c_actionVisionAlign)
        addActionBox.append(actionVisionAlignBtn)

        elevatorBox = gui.HBox()
        addActionBox.append(elevatorBox)
        elevatorBox.append(gui.Label("Elevator position:"))
        self.elevatorPosInput = gui.SpinBox(1, 1, 3)
        elevatorBox.append(self.elevatorPosInput)

        hatchBox = gui.HBox()
        addActionBox.append(hatchBox)
        actionPickUpHatchBtn = gui.Button('Pick up Hatch')
        actionPickUpHatchBtn.onclick.connect(self.c_actionPickUpHatch)
        hatchBox.append(actionPickUpHatchBtn)
        actionDepositHatchBtn = gui.Button('Deposit Hatch')
        actionDepositHatchBtn.onclick.connect(self.c_actionDepositHatch)
        hatchBox.append(actionDepositHatchBtn)

        cargoBox = gui.HBox()
        addActionBox.append(cargoBox)
        actionPickUpCargoBtn = gui.Button('Pick up Cargo')
        actionPickUpCargoBtn.onclick.connect(self.c_actionPickUpCargo)
        cargoBox.append(actionPickUpCargoBtn)
        actionDepositCargoBtn = gui.Button('Deposit Cargo')
        actionDepositCargoBtn.onclick.connect(self.c_actionDepositCargo)
        cargoBox.append(actionDepositCargoBtn)

        # END ADD ACTION BUTTONS

        controlBox = gui.HBox()
        schedulerBox.append(controlBox)

        manualModeBtn = gui.Button("Manual")
        manualModeBtn.onclick.connect(robot.c_manualMode)
        controlBox.append(manualModeBtn)
        autoModeBtn = gui.Button("Auto")
        autoModeBtn.onclick.connect(robot.c_autoMode)
        controlBox.append(autoModeBtn)
        clearScheduleBtn = gui.Button("Clear")
        clearScheduleBtn.onclick.connect(self.c_clearSchedule)
        controlBox.append(clearScheduleBtn)

        schedulerBox.append(gui.Label("Schedule:"))

        self.schedulerList = gui.ListView()
        self.schedulerList.onselection.connect(self.c_removeAction)
        schedulerBox.append(self.schedulerList)

        return schedulerBox

    def initTestControl(self, robot):
        testBox = gui.VBox()
        self.groupStyle(testBox)
        testBox.append(gui.Label("TEST MODE"))

        logBox = gui.HBox()
        testBox.append(logBox)

        logOpticalBtn = gui.Button("Log Optical")
        logOpticalBtn.onclick.connect(robot.c_logOpticalSensors)
        logBox.append(logOpticalBtn)

        swerveBox = gui.HBox()
        testBox.append(swerveBox)

        homeSwerveBtn = gui.Button("Home swerve")
        homeSwerveBtn.onclick.connect(robot.c_homeSwerveWheels)
        swerveBox.append(homeSwerveBtn)

        resetSwerveBtn = gui.Button("Wheels to zero")
        resetSwerveBtn.onclick.connect(robot.c_wheelsToZero)
        swerveBox.append(resetSwerveBtn)

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

    # WIDGET CALLBACKS

    def c_closeApp(self, button):
        self.close()

    def c_setRobotPosition(self, button):
        coord = self.selectedCoord
        self.robot.pathFollower.setPosition(
            coord.x, coord.y, coord.orientation)

    def c_actionDriveToPoint(self, button):
        speed = float(self.speedInput.get_value())
        self.robot.autoScheduler.actionList.append(
            auto_actions.createDriveToPointAction(
                self.robot.pathFollower, self.selectedCoord, speed))
        self.updateScheduler()

    def c_actionNavigate(self, button):
        speed = float(self.speedInput.get_value())
        self.robot.autoScheduler.actionList.append(
            auto_actions.createNavigateToPointAction(
                self.robot.pathFollower, self.selectedCoord, speed))
        self.updateScheduler()

    def c_actionVisionAlign(self, button):
        self.robot.autoScheduler.actionList.append(
            auto_actions.createVisionAlignAction(
                self.robot.superDrive, self.robot.vision))
        self.updateScheduler()

    def c_actionPickUpHatch(self, button):
        self.robot.autoScheduler.actionList.append(
            auto_actions.createPickUpHatchAction(
                self.robot.superDrive, self.robot.grabberArm))
        self.updateScheduler()

    def c_actionDepositHatch(self, button):
        pos = int(self.elevatorPosInput.get_value())
        self.robot.autoScheduler.actionList.append(
            auto_actions.createDepositHatchAction(
                self.robot.superDrive, self.robot.grabberArm, pos))
        self.updateScheduler()

    def c_actionPickUpCargo(self, button):
        self.robot.autoScheduler.actionList.append(
            auto_actions.createPickUpCargoAction(
                self.robot.superDrive, self.robot.grabberArm))
        self.updateScheduler()

    def c_actionDepositCargo(self, button):
        pos = int(self.elevatorPosInput.get_value())
        self.robot.autoScheduler.actionList.append(
            auto_actions.createDepositCargoAction(
                self.robot.superDrive, self.robot.grabberArm, pos))
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
