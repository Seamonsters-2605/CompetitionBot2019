import seamonsters as sea
import remi
from remi import start,App
import remi.gui as gui
class MenuExplore(remi.App):
    
    def __init__(self,*args):
        self.lbls = ['dino','werewolf','monster']
        super(MenuExplore,self).__init__(*args)

    def main(self):
        self.root = gui.VBox(width=500,height=500)
        self.menuItems = []
        for events in self.lbls:
            checkBox = gui.CheckBoxLabel("remove",checked=True)
            checkBox.set_on_click_listener(self.xBoxCallback)
            self.menuItems.append(gui.MenuItem(events,checkBox))
        
        self.eventMenu = gui.Menu(self.menuItems)
        self.buttonToAdd = gui.Button('Add Item')
        self.addedEventIndex = gui.TextInput()
        self.buttonToAdd.set_on_click_listener(self.buttonToAddCallback)
        
        mainHBox = sea.hBoxWith(self.eventMenu,self.buttonToAdd,self.addedEventIndex)
        self.root.append(mainHBox)
        return self.root

    def addItem(self,label,index):
        checkBox = gui.CheckBoxLabel("remove",checked=True)
        checkBox.set_on_click_listener(self.xBoxCallback)
        item = gui.MenuItem(label,checkBox)
        self.menuItems.insert(index,item)
        #return self.eventMenu.append(item)
        self.eventMenu.empty()
        for menuitem in self.menuItems:
            self.eventMenu.append(menuitem)
        print(self.menuItems)

    def xBoxCallback(self,checkBox):
        boxMenuItem = checkBox.get_parent().get_parent()
        checkBox.set_value(not checkBox.get_value())
        self.eventMenu.remove_child(boxMenuItem)
        self.menuItems.remove(boxMenuItem)

    def buttonToAddCallback(self,button):
        try:
            queuePos = int(self.addedEventIndex.get_value())
        except ValueError:
            print('Invalid input to Add Item!')
            return

            
        if queuePos > len(self.menuItems):
            queuePos = len(self.menuItems)
        elif queuePos < 0:
            queuePos = 0
        print(f'queuePos: {queuePos}')
        self.addItem('Event',queuePos)
        
if __name__ == '__main__':
    start(MenuExplore)