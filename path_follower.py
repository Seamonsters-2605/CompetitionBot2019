import numpy
from PIL import Image

pic = Image.open("field.png")
field = numpy.array(pic.getdata(), numpy.uint8).reshape(pic.size[1], pic.size[0], 3)

#the field is 27 by 54 feet

#TODO: allow user to input picture of feild with all obstacles shaded in that becomes converted to the field list

initPos = [9, 9]#TODO: get location of robot and put here, also shift all values over because this has origin in top left but feild in the middle
targetPos = [0, 0]#TODO: get the location of cursor and put here
cost = 1

#has the cost of the robot going away from the goal mapped out so it will only check high cost stuff if there are no other options
heuristic = [[0 for row in range(len(field[0]))] for col in range(len(field))]
for i in range(len(field)):    
    for j in range(len(field[0])):            
        heuristic[i][j] = abs(i - targetPos[0]) + abs(j - targetPos[1])
        if field[i][j][0] != 255:
            heuristic[i][j] = 100 #if there is an obstacle in the spot on the field, adds a very high cost to going over that spot so it will be navigated around

#moves we can go for navigating
moves = [[-1, 0 ], #up
         [ 0, -1], #left
         [ 1, 0 ], #down
         [ 0, 1 ]] #right


#function to search the path
def search(field,initPos,targetPos,cost,heuristic):

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
                if x2 >= 0 and x2 < len(field) and y2 >=0 and y2 < len(field[0]):
                    if refField[x2][y2] == 0 and field[x2][y2][0] == 255:
                        g2 = g + cost
                        f2 = g2 + heuristic[x2][y2]
                        cell.append([f2, g2, x2, y2])
                        refField[x2][y2] = 1
                        actField[x2][y2] = i
                        
    revPath = []
    x = targetPos[0]
    y = targetPos[1]
    revPath.append([x, y])#the steps that must be taken to get to the target (in backwards order)
    while x != initPos[0] or y != initPos[1]:
        x2 = x - moves[actField[x][y]][0]
        y2 = y - moves[actField[x][y]][1]
        x = x2
        y = y2
        revPath.append([x, y])

    path = []
    for i in range(len(revPath)):
    	path.append(revPath[len(revPath) - 1 - i])

    return path

def navigate():
    return search(field, initPos, targetPos, cost, heuristic)

print(navigate())