import seamonsters as sea

class Action:

    def __init__(self, name, generator, coords=[]):
        self.name = name
        self.generator = generator
        self.coords = coords

class AutoScheduler:

    def __init__(self):
        self.actionList = []
        self.runningAction = None
        self.paused = False
        self.updateCallback = lambda: None
        self._actionCancelled = False

    def updateGenerator(self):
        while True:
            if len(self.actionList) != 0 and not self.paused:
                self.runningAction = self.actionList.pop(0)
                print("Running action " + self.runningAction.name)
                self.updateCallback()
                yield from sea.parallel(
                    sea.stopAllWhenDone(self.runningAction.generator),
                    sea.stopAllWhenDone(self._watchForCancelGenerator()))
                print("Finished action " + self.runningAction.name)
                self.runningAction = None
                self.updateCallback()
            else:
                yield

    def clearActions(self):
        self.cancelRunningAction()
        self.actionList.clear()

    def cancelRunningAction(self):
        self._actionCancelled = True

    def _watchForCancelGenerator(self):
        while not self._actionCancelled:
            yield
        self._actionCancelled = False
