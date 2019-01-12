import seamonsters as sea
from auto_scheduler import Action

def createTestAction(time):
    return Action("Wait " + str(time), sea.wait(time))
