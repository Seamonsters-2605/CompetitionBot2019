import seamonsters as sea
from auto_scheduler import Action

def createWaitAction(time):
    return Action("Wait " + str(time), sea.wait(int(time * 50)))
