import seamonsters as sea

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