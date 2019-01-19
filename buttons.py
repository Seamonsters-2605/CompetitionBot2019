import ctre
import wpilib
from enum import Enum
import time

class Buttons():    

    def __init__(self):
        self.SINGLE_CLICK = 1
        self.DOUBLE_CLICK = 2
        self.HELD = 3
        self.joystick = wpilib.Joystick(0)
        self.presets = []
        self.doubleClickDetector = {}

    def addPreset(self, button, clickType, function, args):
        self.presets.append((button, clickType, function, args))

    def update(self):
        for button, clickType, function, args in self.presets:
            if self.joystick.getRawButtonPressed(button) and clickType == self.SINGLE_CLICK:
                function(*args)
            elif self.joystick.getRawButton(button) and clickType == self.HELD:
                function()
            elif clickType == self.DOUBLE_CLICK:
                if self.doubleClickDetector.get(button) == None:
                    self.doubleClickDetector[button] = time.time
                if time.time + 0.25 > self.doubleClickDetector[button]:
                    self.doubleClickDetector[button] = time.time
                    function()  
                else:
                    self.doubleClickDetector[button] = time.time             