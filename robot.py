import math
import wpilib
import ctre
import navx
import seamonsters as sea
import drivetrain
import dashboard
import grabber
from buttons import Buttons
import auto_scheduler
import auto_actions
import coordinates
from networktables import NetworkTables

class CompetitionBot2019(sea.GeneratorBot):

    def robotInit(self):

        self.grabberArm = grabber.GrabberArm()

        self.grabberArm.startCompressor()

        self.joystick = wpilib.Joystick(0)

        self.superDrive = drivetrain.initDrivetrain()
        self.drivegear = None
        self.headless_mode = False
        
        self.ahrs = navx.AHRS.create_spi()
        self.pathFollower = sea.PathFollower(self.superDrive, self.ahrs)

        self.joystick = wpilib.Joystick(0)
        self.button = Buttons(self.joystick)
        self.button.addPreset(3,Buttons.SINGLE_CLICK, self.switchHeadless, [])

        self.pdp = wpilib.PowerDistributionPanel(50)
        self.testDIO = wpilib.DigitalInput(0)

        self.autoScheduler = auto_scheduler.AutoScheduler()
        self.autoScheduler.updateCallback = self.updateScheduler

        self.timingMonitor = sea.TimingMonitor()

        self.vision = NetworkTables.getTable('limelight')

        self.app = None # dashboard
        sea.startDashboard(self, dashboard.CompetitionBotDashboard)

        self.button = Buttons(self.joystick) 
        self.button.addPreset(1,Buttons.HELD, self.grabberArm.grabBall, [1,1])
        self.button.addPreset(1,Buttons.NOT_HELD,self.grabberArm.stop,[])
        self.button.addPreset(4,Buttons.SINGLE_CLICK, self.switchHeadless, [])
        self.button.addPreset(2,Buttons.HELD,self.grabberArm.releaseBall,[1,1])
        self.button.addPreset(2,Buttons.NOT_HELD,self.grabberArm.stop,[])
        self.button.addPreset(6,Buttons.HELD,self.grabberArm.pull,[])
        self.button.addPreset(6,Buttons.NOT_HELD,self.grabberArm.stopPulling,[])
        self.button.addPreset(7,Buttons.HELD,self.grabberArm.push,[])
        self.button.addPreset(7,Buttons.NOT_HELD,self.grabberArm.stopPushing,[])


    def updateScheduler(self):
        if self.app is not None:
            self.app.updateScheduler()

    def resetPositions(self):
        for wheel in self.superDrive.wheels:
            wheel.resetPosition()

    def setGear(self, gear):
        if gear == self.drivegear:
            return
        self.drivegear = gear
        for wheel in self.superDrive.wheels:
            wheel.angledWheel.driveMode = gear.mode
            wheelMotor = wheel.angledWheel.motor
            wheelMotor.config_kP(0, self.drivegear.p, 0)
            wheelMotor.config_kI(0, self.drivegear.i, 0)
            wheelMotor.config_kD(0, self.drivegear.d, 0)
            wheelMotor.config_kF(0, self.drivegear.f, 0)
        if self.app is not None:
            self.app.driveGearLbl.set_text("Gear: " + str(gear))

    def teleop(self):
        self.setGear(drivetrain.mediumPositionGear)
        self.resetPositions()
        self.pathFollower.setPosition(0, 0, 0)
        yield from sea.parallel(self.joystickControl(),
            self.basicUpdateLoop(), self.timingMonitor.updateGenerator())
    
    def autonomous(self):
        self.setGear(drivetrain.mediumPositionGear)
        self.resetPositions()
        self.pathFollower.setPosition(0, 0, 0)
        self.superDrive.drive(0,0,0)
        yield from sea.parallel(self.autoScheduler.updateGenerator(),
            self.basicUpdateLoop(), self.timingMonitor.updateGenerator())

    def basicUpdateLoop(self):
        if self.app is not None:
            self.app.clearEvents()
        while True:
            if self.app is not None:
                self.app.doEvents()
            self.updateDashboardLabels()
            yield

    def joystickControl(self):
        while True:
            self.pathFollower.updateRobotPosition()

            x = self.joystick.getX()
            y = self.joystick.getY()
            mag = sea.deadZone(math.hypot(x * (1 - 0.5*y**2) ** 0.5,y * (1 - 0.5*x**2) ** 0.5))
            mag *= self.drivegear.moveScale

            direction = -self.joystick.getDirectionRadians() + math.pi/2

            if self.headless_mode:
                direction -= self.pathFollower.robotAngle
            
            turn = -sea.deadZone(self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_TWIST)
                + 0.5 * self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_LEVER))
            turn *= self.drivegear.turnScale # maximum radians per second

            self.grabberArm.slide(-self.joystick.getRawAxis(sea.TFlightHotasX.AXIS_THROTTLE))

            if not self.joystick.getPOV() == -1:
                aDiff = sea.circleDistance(-math.radians(self.joystick.getPOV()) + math.pi, self.pathFollower.robotAngle)
                turn = aDiff / 0.1 # seconds
                targetAVel = drivetrain.fastPositionGear.turnScale
                if turn > targetAVel:
                    turn = targetAVel
                elif turn < -targetAVel:
                    turn = -targetAVel

            self.superDrive.drive(mag, direction, turn)
            
            if self.app != None:
                self.app.updateBrokenEncoderButton(self)

            self.button.update()

            yield

    def updateDashboardLabels(self):
        if self.app != None:
            self.app.updateRobotPosition(
                self.pathFollower.robotX, self.pathFollower.robotY,
                self.pathFollower.robotAngle)
            self.app.realTimeRatioLbl.set_text(
                '%.3f' % (self.timingMonitor.realTimeRatio,))
            self.app.currentLbl.set_text(str(self.pdp.getTotalCurrent()))

            encoderString = ''
            for wheel in self.superDrive.wheels:
                encoderString += '%.3f ' % math.degrees(wheel._getCurrentSteeringAngle())
            self.app.encoderLbl.set_text(encoderString)

    def toggleAutoScheduler(self):
        if self.autoScheduler.isPaused():
            self.autoScheduler.unpause()
        else:
            self.autoScheduler.pause()

    # button functions

    def switchHeadless(self):
        if self.headless_mode == False:
            self.headless_mode = True
            print("Headless Mode On")
        else:
            self.headless_mode = False
            print("Headless Mode Off")

    # dashboard callbacks

    @sea.queuedDashboardEvent
    def c_addWaitAction(self, button):
        waitTime = float(self.app.waitTimeInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createWaitAction(waitTime))
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_addDriveToPointAction(self, button):
        pointX = self.app.selectedCoord.x
        pointY = self.app.selectedCoord.y
        pointAngle = self.app.selectedCoord.orientation
        moveTime = float(self.app.waitTimeInput.get_value())
        self.autoScheduler.actionList.append(
            auto_actions.createDriveToPointAction(self.pathFollower, pointX, pointY, pointAngle, moveTime))
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_addNavigateAction(self, button):
        coord = self.app.selectedCoord
        waypoints = coordinates.findWaypoints(coord, self.pathFollower.robotX, self.pathFollower.robotY)
        moveTime = float(self.app.waitTimeInput.get_value())
        for pt in waypoints:
            action = auto_actions.createDriveToPointAction(self.pathFollower, pt.x, pt.y, pt.orientation, moveTime)
            self.autoScheduler.actionList.append(action)
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_addVisionAlignAction(self, button):
        self.autoScheduler.actionList.append(auto_actions.createVisionAlignAction(self.superDrive, self.vision))
        self.updateScheduler()

    @sea.queuedDashboardEvent
    def c_pauseScheduler(self, button):
        self.autoScheduler.pause()

    @sea.queuedDashboardEvent
    def c_resumeScheduler(self, button):
        self.autoScheduler.unpause()

    @sea.queuedDashboardEvent
    def c_wheelsToZero(self, button):
        for wheel in self.superDrive.wheels:
            wheel._setSteering(0)

    @sea.queuedDashboardEvent
    def c_resetPosition(self, button):
        self.pathFollower.setPosition(
            self.app.selectedCoord.x, self.app.selectedCoord.y, self.app.selectedCoord.orientation)

    @sea.queuedDashboardEvent
    def c_slowVoltageGear(self, button):
        self.setGear(drivetrain.slowVoltageGear)

    @sea.queuedDashboardEvent
    def c_mediumVoltageGear(self, button):
        self.setGear(drivetrain.mediumVoltageGear)

    @sea.queuedDashboardEvent
    def c_fastVoltageGear(self, button):
        self.setGear(drivetrain.fastVoltageGear)

    @sea.queuedDashboardEvent
    def c_slowPositionGear(self, button):
        self.setGear(drivetrain.slowPositionGear)

    @sea.queuedDashboardEvent
    def c_mediumPositionGear(self, button):
        self.setGear(drivetrain.mediumPositionGear)

    @sea.queuedDashboardEvent
    def c_fastPositionGear(self, button):
        self.setGear(drivetrain.fastPositionGear)

    @sea.queuedDashboardEvent
    def c_disableWheel(self, button):
        self.superDrive.wheels[button.wheelNum - 1].angledWheel.driveMode = ctre.ControlMode.Disabled
        self.app.switchDeadWheelText(button)

    @sea.queuedDashboardEvent
    def c_toggleAutoScheduler(self, button):
        self.app.toggleAutoScheduler(button)
        self.toggleAutoScheduler()

    @sea.queuedDashboardEvent
    def c_clearAll(self, button):
        self.autoScheduler.clearActions()
        self.app.updateScheduler()
    
    @sea.queuedDashboardEvent
    def c_cancelRunningAction(self, button):
        self.autoScheduler.cancelRunningAction()

if __name__ == "__main__":
    wpilib.run(CompetitionBot2019)