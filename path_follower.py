import numpy
from PIL import Image

#you must download pillow and numpy!!!

class PathFinder:

    def __init__(self, fieldImage):
        """
        :param fieldImage: the file location of an image of the field where all places with obstacles
        have been filled in black and it has the pixel dimensions 1:1 of the field in feet
        """
        pic = Image.open(fieldImage)
        self.field = numpy.array(pic.getdata(), numpy.uint8).reshape(pic.size[1], pic.size[0], 4)

    #function to search the path
    def search(self,field,initPos,targetPos,cost,heuristic):

        #moves we can go for navigating
        moves = [[-1, 0 ], #up
                [ 0, -1], #left
                [ 1, 0 ], #down
                [ 0, 1 ]] #right

        refField = [[0 for col in range(len(field[0]))] for row in range(len(field))]#the referrence field
        refField[initPos[0]][initPos[1]] = 1
        actField = [[0 for col in range(len(field[0]))] for row in range(len(field))]#the field where the action happens 

        x = initPos[0]
        y = initPos[1]
        g = 0
        f = g + heuristic[initPos[0]][initPos[0]]
        cell = [[f, g, x, y]]

        found = False  #becomes true when robot gets to target position

        while not found:
            cell.sort()#rearrange list to get the move with the least cost
            cell.reverse()
            next = cell.pop()
            x = next[2]
            y = next[3]
            g = next[1]
            f = next[0]

            
            if x == targetPos[0] and y == targetPos[1]:
                found = True
            else:
                for i in range(len(moves)):#to try out different moves
                    x2 = x + moves[i][0]
                    y2 = y + moves[i][1]
                    if x2 >= 0 and x2 < len(field) and y2 >= 0 and y2 < len(field[0]):
                        if refField[x2][y2] == 0 and field[x2][y2][0] == 255:
                            g2 = g + cost
                            f2 = g2 + heuristic[x2][y2]
                            cell.append([f2, g2, x2, y2])
                            refField[x2][y2] = 1
                            actField[x2][y2] = i
                                
        path = []
        x = targetPos[0]
        y = targetPos[1]
        path.append([x, y])
        while x != initPos[0] or y != initPos[1]:#makes path in backwards
            x2 = x - moves[actField[x][y]][0]
            y2 = y - moves[actField[x][y]][1]
            x = x2
            y = y2
            path.append([x, y])

        for i in range(len(path)):#reverse path back to normal
            temp = path[i]
            path[i] = path[len(path) - 1 - i]
            path[len(path) - 1 - i] = temp

        return path

    def navigate(self, initPos, targetPos):
        """
        :param initPos: a 2 element list of the current position of the robot [x,y]
        :param initPos: a 2 element list of the position that we want the robot to go to [x,y]
        """
        cost = 1

        # has the cost of the robot going away from the goal mapped out so it will only check high cost 
        # stuff if there are no other options
        heuristic = [[0 for row in range(len(self.field[0]))] for col in range(len(self.field))]
        for i in range(len(self.field)):    
            for j in range(len(self.field[0])):            
                heuristic[i][j] = abs(i - targetPos[0]) + abs(j - targetPos[1])
                if self.field[i][j][0] != 255:
                    heuristic[i][j] = 100 # if there is an obstacle in the spot on the field, adds a very high 
                    # cost to going over that spot so it will be navigated around
        startPos = [0,0]
        startPos[0] = initPos[1] + int(len(self.field)/2)
        startPos[1] = initPos[0] + int(len(self.field[0])/2)
        endPos = [0,0]                                
        endPos[0] = targetPos[1] + int(len(self.field)/2)#compensating for difference in origin 
        endPos[1] = targetPos[0] + int(len(self.field[0])/2)#(this is top left but dashboard is very middle)
        return self.search(self.field, startPos, endPos, cost, heuristic)

test = PathFinder("field.png")
print(test.navigate([0, -5], [0, 5]))