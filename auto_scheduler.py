import seamonsters as sea
import coordinates

class Action(sea.State):

    def __init__(self, name, function, key, coords=[], driveCoordinate=[]):
        self.name = name
        self.function = function
        self.coords = coords
        self.key = key
        self.driveCoordinate = driveCoordinate

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
            newAction = {
                    "key" : action.key,
                    "coord" : []
                }
            if action.driveCoordinate != []:
                newAction["coord"] = [action.driveCoordinate[0][0], action.driveCoordinate[0][1], action.driveCoordinate[0][2], \
                    action.driveCoordinate[0][3], action.driveCoordinate[0][4]]
            schedulePreset.append(newAction)
        return schedulePreset