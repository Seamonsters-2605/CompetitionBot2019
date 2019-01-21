import ctre
import wpilib
import time

class Buttons():    

    def __init__(self):
        self.SINGLE_CLICK = 1
        self.DOUBLE_CLICK = 2
        self.HELD = 3
        self.NOT_HELD = 4
        self.joystick = wpilib.Joystick(0)
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
            if self.joystick.getRawButtonPressed(button) and clickType == self.SINGLE_CLICK:
                function(*args)
            elif self.joystick.getRawButton(button) and clickType == self.HELD:
                function(*args)
            elif not (self.joystick.getRawButton(button)) and clickType == self.NOT_HELD:
                function(*args)
            elif clickType == self.DOUBLE_CLICK:
                if self.doubleClickDetector.get(button) == None:
                    self.doubleClickDetector[button] = time.time
                if time.time + 0.25 > self.doubleClickDetector[button]:
                    self.doubleClickDetector[button] = time.time
                    function(*args)  
                else:
                    self.doubleClickDetector[button] = time.time             