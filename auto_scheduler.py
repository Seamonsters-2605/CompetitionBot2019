import seamonsters as sea
import coordinates

class Action(sea.State):

    def __init__(self, name, function, coords=[]):
        self.name = name
        self.function = function
        self.coords = coords

class AutoScheduler:

    def __init__(self):
        self.actionList = []
        self.runningAction = None
        self.updateCallback = lambda: None
        self.idleFunction = lambda: None

    def runSchedule(self):
        try:
            while True:
                if len(self.actionList) == 0:
                    self.runningAction = None
                    self.updateCallback()
                    while len(self.actionList) == 0:
                        self.idleFunction()
                        yield
                        continue
                self.runningAction = self.actionList[0]
                self.updateCallback()
                yield from self.runningAction.function()
                self.actionList.remove(self.runningAction)
        finally:
            self.runningAction = None

    def toJson(self):
        schedulePreset = []
        for action in self.actionList:
            coordinate = [action.coords.name, action.coords.x, action.coords.y, \
                action.coords.orientation, action.coords.angle, action.coords.visionTarget]
            schedulePreset.append(
                {
                    "name" : action.name,
                    "coords" : coordinate
                }
            )
        return schedulePreset

    def toSchedule(self, jSched):
        for action in jSched:
            coordinate = coordinates.DriveCoordinate(action["coords"][0], action["coords"][1], action["coords"][2], \
                action["coords"][3], action["coords"][4]) 
            realAction = Action(action.name, """not sure what to put here yet""", coordinate)
            self.actionList.append(realAction)