import ctre
import wpilib
import time

class Buttons():    

    SINGLE_CLICK = 1
    DOUBLE_CLICK = 2
    HELD = 3
    NOT_HELD = 4

    def __init__(self, joystick, doubleClickDelay = 0.25):
        self.doubleClickDelay = doubleClickDelay
        self.joystick = joystick
        self.presets = []
        self.otherPresets = []
        self.doubleClickDetector = {}

    def addPreset(self, button, clickType, function, args):
        self.presets.append((button, clickType, function, args))

    def removePreset(self, button, clickType, function, args):
        self.presets.remove((button, clickType, function, args))

    def switchPreset(self):
        self.temp = self.presets
        self.presets = self.otherPresets
        self.otherPresets = self.temp

    def update(self):
        for button, clickType, function, args in self.presets:
            if clickType == Buttons.SINGLE_CLICK and self.joystick.getRawButtonPressed(button):
                function(*args)
            elif clickType == Buttons.HELD and self.joystick.getRawButton(button):
                function(*args)
            elif clickType == Buttons.NOT_HELD and not (self.joystick.getRawButton(button)):
                function(*args)
            elif clickType == Buttons.DOUBLE_CLICK:
                if self.doubleClickDetector.get(button) == None:
                    self.doubleClickDetector[button] = time.time
                if time.time + self.doubleClickDelay > self.doubleClickDetector[button]:
                    self.doubleClickDetector[button] = time.time
                    function(*args)  
                else:
                    self.doubleClickDetector[button] = time.time             