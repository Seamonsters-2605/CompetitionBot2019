import remi.gui as gui
import seamonsters as sea

class SwerveBotDashboard(sea.Dashboard):
    
    def main(self, robot, appCallback):
        self.robot = robot

        root = gui.VBox(width=600)
        buttons = [] 
        rowBoxes = []
        self.wheelClsButton = dict() # superHolonomicDrive AngledWheel:wheelButton
        for num,wheel in enumerate(robot.superDrive.wheels):
            wheelButton = gui.Button(text=f"Wheel {num}")
            buttons.append(wheelButton)
            self.wheelClsButton[wheel] = wheelButton

        for num,button in enumerate(buttons):
            button.onclick.connect(self.onButtonPressed)
        
        rowLen = 2   
        buttonStat = [] # button, statbox     
        for i in buttons:
            statLabels = [gui.Label(stat) for stat in ['stat 1','stat 2','stat 3']]
            statBox = sea.vBoxWith(i,statLabels)
            buttonStat.append(statBox)

        for i in [j for j in range(len(buttonStat)) if j % rowLen == 0]:
            box = sea.hBoxWith(*buttonStat[i : i + rowLen])
            rowBoxes.append(box)
        root.append(rowBoxes)
        appCallback(self)
        return root

    def onButtonPressed(self,button):
        button.style['background'] = 'black'
        for k in self.wheelClsButton.keys():
            if self.wheelClsButton[k] == button:
                k.stop()
                print(k,"is stopped")
        
    def updateMotorStatus(self,wheel):
        if wheel.encoderWorking:
                self.wheelClsButton[wheel].style['background'] = 'green'
        else:
            self.wheelClsButton[wheel].style['background'] = 'red'
        