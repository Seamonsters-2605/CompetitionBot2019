import seamonsters as sea

class Action(sea.State):

    def __init__(self, name, function, coords=[]):
        super().__init__(function)
        self.name = name
        self.coords = coords

class AutoScheduler:

    PAUSE_STATE = sea.State(sea.forever)

    def __init__(self):
        self.stateMachine = sea.StateMachine()
        self.actionList = []
        self.runningAction = None
        self.updateCallback = lambda: None

        self.stateMachine.push(sea.State(self._actionScheduler))

    def updateGenerator(self):
        yield from self.stateMachine.updateGenerator()

    def _actionScheduler(self):
        if len(self.actionList) == 0:
            self.runningAction = None
            self.updateCallback()
            while len(self.actionList) == 0:
                yield
        self.runningAction = self.actionList.pop(0)
        print("Running action " + self.runningAction.name)
        self.updateCallback()
        return self.runningAction

    def cancelRunningAction(self):
        if isinstance(self.stateMachine.currentState(), Action):
            self.stateMachine.pop()

    def clearActions(self):
        self.actionList.clear()
        self.cancelRunningAction()

    def pause(self):
        if not self.isPaused():
            self.stateMachine.push(AutoScheduler.PAUSE_STATE)

    def unpause(self):
        if self.isPaused():
            self.stateMachine.pop()

    def isPaused(self):
        return self.stateMachine.currentState() == AutoScheduler.PAUSE_STATE
