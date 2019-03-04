import pygame, sys, math, random, NrNt
from pygame.locals import *
from enum import Enum
random.seed(250)

class TileColor(Enum):
    GRAY   = 0
    BLUE   = 1
    ORANGE = 2
    YELLOW = 3
    TEAL   = 4
    RED    = 5
    PURPLE = 6
    GREEN  = 7
    
class TileType(Enum):
    LINE = 0
    L = 1
    IL = 2
    SQUARE = 3
    Z = 4
    IZ = 5
    T = 6
    
TileTypeColors = {
    TileType.LINE: TileColor.TEAL,
    TileType.L: TileColor.ORANGE,
    TileType.IL: TileColor.BLUE,
    TileType.SQUARE: TileColor.YELLOW,
    TileType.Z: TileColor.RED,
    TileType.IZ: TileColor.GREEN,
    TileType.T: TileColor.PURPLE
    }
    
TileShapes = {
    TileType.LINE: [(1,0), (-2, 0), (-1,0)],
    TileType.L: [(1, 0), (-1, 0), (1, -1)],
    TileType.IL: [(1, 0), (-1, 0), (-1, -1)],
    TileType.SQUARE: [(-1, 0), (0, 1), (-1, 1)],
    TileType.Z: [(-1, 0), (0, -1), (1, -1)],
    TileType.IZ: [(1, 0), (0, -1), (-1, -1)],
    TileType.T: [(-1, 0), (0, -1), (1, 0)]
    }

CONST_BlockSize = 25
CONST_ScreenSizeX = 600
CONST_ScreenSizeY = 600
CONST_GameDimX = 10
CONST_GameDimY = 20
CONST_NumFuture = 2
TickTime = 0.5

class Block:
    gridPos = None
    blockColor = None
    rect = None
    origin = None
    
    # Initializes block
    def __init__(self, origin, gPos, color):
        self.gridPos = gPos
        self.blockColor = color
        self.origin = origin
        pos = self.getPixelPos()
        self.rect = pygame.Rect(pos[0], pos[1], CONST_BlockSize, CONST_BlockSize)
        
    # Returns the position that the block should be drawn at; Returns tuple of x,y
    def getPixelPos(self):
        x = self.origin[0] + self.gridPos[0]*CONST_BlockSize
        y = self.origin[1] - self.gridPos[1]*CONST_BlockSize
        return (x, y)
    
    # Returns the grid position the block would be if rotated around otherPos by rotAmount
    def getRotatedPos(self, otherPos, rotAmount, blockType):
        tempPos = [self.gridPos[0] + 0.5, self.gridPos[1] - 0.5]
        radians = math.radians(rotAmount)
        s = math.sin(radians)
        c = math.cos(radians)
        tempPos[0] -= otherPos[0]
        tempPos[1] -= otherPos[1]
        xNew = tempPos[0] * c - tempPos[1] * s
        yNew = tempPos[0] * s + tempPos[1] * c
        tempPos[0] = round(xNew + otherPos[0] - 0.5)
        tempPos[1] = round(yNew + otherPos[1] + 0.5)
        return tempPos
    
    # Returns true if can move (x, y) blocks without colliding in game
    def canMove(self, movement, game):
        newPos = (self.gridPos[0] + movement[0], self.gridPos[1] + movement[1])
        return not game.checkCollision(newPos)
            
    # Forces rotation to new grid position based on getRotatedPos
    def rotate(self, otherPos, rotAmount, blockType):
        pos = self.getRotatedPos(otherPos, rotAmount, blockType)
        self.gridPos = (pos[0], pos[1])
    
    def draw(self):
        pos = self.getPixelPos()
        display.blit(tileImgs[self.blockColor], pos)
    
class Shape:
    origin = None
    myBlocks = None
    myType = None
    myCenter = None
    myGame = None
    currentRotation = 0
    
    def __init__(self, tileType, gridCenter, origin, game):
        self.myType = tileType
        self.origin = origin
        self.myGame = game
        self.currentRotation = 0
        
        if tileType != TileType.LINE and tileType != TileType.SQUARE:
            self.myCenter = (gridCenter[0] + 0.5, gridCenter[1] + 0.5)
        else:
            self.myCenter = gridCenter
            
        self.initializeBlockType()
        
    # Initializes myBlocks with appropriate blocks based on myType
    def initializeBlockType(self):
        self.myBlocks = []
        center = (math.floor(self.myCenter[0]), math.ceil(self.myCenter[1]))
        
        initShape = TileShapes[self.myType]
        self.myBlocks.append(Block(self.origin, center, TileTypeColors[self.myType]))
        for i in range(len(initShape)):
            self.myBlocks.append(Block(self.origin, (center[0]+initShape[i][0], center[1]+initShape[i][1]), TileTypeColors[self.myType]))
        
    # Tries to rotate all blocks of shape
    def rotate(self, direction, *it):
        positions = []
        requiredMovement = [0, 0]
        for block in self.myBlocks:
            positions.append(block.getRotatedPos(self.myCenter,90*direction,self.myType))
        requiredMovement = self.getRequiredMove(positions, self.myCenter)
        
        if requiredMovement != False:
            self.currentRotation += direction
            self.currentRotation %= 4
            self.myCenter = (self.myCenter[0]+requiredMovement[0], self.myCenter[1]+requiredMovement[1])
            for i in range(len(positions)):
                positions[i] = (positions[i][0] + requiredMovement[0], positions[i][1] + requiredMovement[1])
            for i in range(len(self.myBlocks)):
                self.myBlocks[i].gridPos = positions[i]
                                                                                                                                                                                                                                                                                                                                                                            
    # Returns (x, y) of required movement in order to avoid collision
    def getRequiredMove(self, positions, center, *recurs):
        if len(recurs)!=0:
            for pos in positions:
                if self.myGame.checkCollision(pos):
                    return False
            return True
        elif len(recurs) == 0:
            shortest = (-2, -2)
            for x in range(-2, 3):
                for y in range(-2, 3):
                    temp = positions.copy()
                    for i in range(len(temp)):
                        temp[i] = (temp[i][0] + x, temp[i][1] + y)
                    move = self.getRequiredMove(temp, (self.myCenter[0] + x, self.myCenter[1] + y), False)
                    if move:
                        dist = abs(x) + abs(y)
                        shortDist = abs(shortest[0]) + abs(shortest[1])
                        if dist < shortDist:
                            shortest = (x, y)
            return shortest
            
    # Tries to move shape down; returns true if possible, false if collides
    def tick(self):
        return self.move((0, -1))
            
    # Tries to move shape in dir; returns true if possible, false if collides
    def move(self, direction):
        for block in self.myBlocks:
            if block.canMove(direction, self.myGame) != True:
                return False
        for block in self.myBlocks:
            block.gridPos = (block.gridPos[0]+direction[0], block.gridPos[1]+direction[1])
        self.myCenter = (self.myCenter[0]+direction[0], self.myCenter[1]+direction[1])
        return True
    
    # Forces block to move in dir
    def forceMove(self, direction):
        for block in self.myBlocks:
            block.gridPos = (block.gridPos[0]+direction[0], block.gridPos[1]+direction[1])
        self.myCenter = (self.myCenter[0]+direction[0], self.myCenter[1]+direction[1])
    
    def draw(self):
        for block in self.myBlocks:
            block.draw()
        
    
    
class TetrisGameState:
    currentShape = None
    drawOrigin = None
    blockGrid = None
    outlineBlocks = None
    size = None
    currentQueue = None
    currentQueueBlocks = None
    currentHeld = None
    currentHeldObj = None
    GameOver = False
    linesComplete = 0
    score = 0
    level = 1

    def __init__(self, drawOrigin, size):
        self.drawOrigin = drawOrigin
        self.size = size
        self.blockGrid = []
        self.outlineBlocks = []
        self.currentQueue = []
        self.currentQueueBlocks = []
        self.newShape()
        self.initializeOutline()
        self.addToQueue()
    
    # Returns average of all highest points y
    def getHeight(self):
        total = 0
        for x in range(self.size[0]):
            total += self.getHighestInColumn(x)
        return total / x
        
    def getBumpiness(self):
        bump = 0
        for x in range(1, self.size[0]):
            bump += abs(self.getHighestInColumn(x) - self.getHighestInColumn(x-1))
        return bump
        
    # Returns weighted number of holes in grid
    def getHoles(self):
        realGrid = []
        holeCount = 0
        for y in range(self.size[1]):
            temp = []
            for x in range(self.size[0]):
                temp.append(self.blockExistsAtPos((x, y)))
            realGrid.append(temp)
        for y in range(len(realGrid)):
            for x in range(len(realGrid[0])):
                if self.blocked(realGrid, (x, y+1)):
                    holeCount += 1
                    for y2 in range(1, y):
                        if self.blocked(realGrid, (x, y-y2)):
                            break
                        holeCount += y # Deeper holes are worse
        return holeCount
        
    # Returns true if given pos is blocked
    def blocked(self, arr, pos):
        #print(pos)
        if pos[0] >= len(arr[0]) or pos[0] < 0 or pos[1] >= len(arr) or pos[1] < 0:
            return True
        elif arr[pos[1]][pos[0]] != False:
            return True
        return False
        
    def getFitness(self):
        score = 0
        height = self.getHeight()
        lines = self.linesComplete
        holes = self.getHoles()
        bumpiness = self.getBumpiness()
        score += ((1*height) + (0.76*lines) - (0.36*holes) - (0.4*bumpiness)) + (1*self.score) + (0.2*len(self.blockGrid))
        #for block in self.blockGrid:
        #    score += math.floor((pow((CONST_GameDimY-block.gridPos[1]) * CONST_GameDimY,2))/100000)
        #score += self.score
        return score
        
    # Gets inputs for current game state; 1 for each column, 1 for current blockX, 1 for current block type, 1 for rotation
    def getInputs(self):
        inputs = []
        for i in range(1, CONST_GameDimX):
            inputs.append(self.getHighestInColumn(i) - abs(self.getHighestInColumn(i-1)))
        shapeCenterX = math.floor(self.currentShape.myCenter[0])
        inputs.append(shapeCenterX)
        inputs.append(self.currentShape.myType.value)
        inputs.append(self.currentShape.currentRotation)
        return inputs
        
    def getMostRow(self):
        highest = 0
        for i in range(self.size[1]):
            amt = self.getRowAmt(i)
            if amt == 0:
                return highest
            else:
                if amt > highest:
                    highest = amt
        return highest
        
    def getRowAmt(self, r):
        amt = 0
        for block in self.blockGrid:
            if block.gridPos[1] == r:
                amt += 1
        return amt
        
    # Returns y of highest in column
    def getHighestInColumn(self, c):
        highest = 0
        for block in self.blockGrid:
            if block.gridPos[0] == c:
                if block.gridPos[1] > highest:
                    highest = block.gridPos[1]
        return highest
    
    # Holds current shape, calls next shape if necessary
    def hold(self):
        if self.currentHeld == None:
            self.currentHeld = self.currentShape.myType
            self.currentShape = None
            self.newShape()
            self.buildHeldObj()
        else:
            held = self.currentHeld
            self.currentHeld = self.currentShape.myType
            center = (math.floor(CONST_GameDimX/2), CONST_GameDimY-2)
            self.currentShape = Shape(held, center, self.drawOrigin, self)
            self.buildHeldObj()
    
    # Creates obj for currentHeld
    def buildHeldObj(self):
        if self.currentHeld != None:
            obj = Shape(self.currentHeld, (CONST_GameDimX+3, CONST_GameDimY/2), self.drawOrigin, self)
            self.currentHeldObj = obj
        else:
            self.currentHeldObj = None
    
    # Checks all rows and clears full rows
    def checkClearRows(self):
        lineCount = 0
        y = 0
        while y < self.size[1]:#for y in range(self.size[1]):
            if self.checkRow(y):
                lineCount += 1
                for x in range(self.size[0]):
                    self.blockGrid.remove(self.blockExistsAtPos((x, y)))
                for block in self.blockGrid:
                    if block.gridPos[1] > y:
                        block.gridPos = (block.gridPos[0], block.gridPos[1]-1)
                y-=1
            y += 1
        if lineCount == 1:
            self.score += 40 * self.level
        elif lineCount == 2:
            self.score += 100 * self.level
        elif lineCount == 3:
            self.score += 300 * self.level
        elif lineCount == 4:
            self.score += 1200 * self.level
        self.linesComplete += lineCount
        
    #Returns true if row is full, false otherwise
    def checkRow(self, row):
        for x in range(self.size[0]):
            if self.blockExistsAtPos((x, row)) == False:
                return False
        return True
    
    #Returns true if blcok exists at pos in blockGrid
    def blockExistsAtPos(self, pos):
        for block in self.blockGrid:
            if block.gridPos[0] == pos[0] and block.gridPos[1] == pos[1]:
                return block
        return False
    
    #Returns true when gridpos is in collision with something else
    def checkCollision(self, pos):
        if pos[0] < 0 or pos[0] >= self.size[0] or pos[1] < 0 or pos[1] >= self.size[1]:
            return True
        else:
            for block in self.blockGrid:
                if pos[0] == block.gridPos[0] and pos[1] == block.gridPos[1]:
                    return True
        return False
    
    # Creates new moving shape, populates queue if necessary, calls CheckClearRows
    def newShape(self):
        if self.GameOver == False:
            self.checkClearRows()
            center = (math.floor(CONST_GameDimX/2), CONST_GameDimY-2)
            if len(self.currentQueue) <= CONST_NumFuture:
                self.addToQueue()
            shape = self.currentQueue.pop(0)
            self.currentShape = Shape(shape, center, self.drawOrigin, self)
            for block in self.currentShape.myBlocks:
                if self.checkCollision(block.gridPos):
                    self.GameOver = True
        self.buildQueueObjs()
    
    # Builds new queue objects to show
    def buildQueueObjs(self):
        self.currentQueueBlocks = []
        queuePos = (-4, CONST_GameDimY-5)
        for i in range(CONST_NumFuture):
            shape = self.currentQueue[i]
            self.currentQueueBlocks.append(Shape(shape, (queuePos[0], queuePos[1] - (i*3)), self.drawOrigin, self))
            
    
    #Adds a random order of 2*shapelist number of shapes to queue
    def addToQueue(self):
        shapeList = []
        for s in TileType:
            shapeList.append(s)
            shapeList.append(s)
        random.shuffle(shapeList)
        for s in shapeList:
            self.currentQueue.append(s)
            
    def tick(self):
        if self.currentShape.tick() == False:
            for block in self.currentShape.myBlocks:
                self.blockGrid.append(block)
            self.newShape()
            
    def tickUntilNewShape(self):
        curr = self.currentShape
        while curr == self.currentShape:
            self.tick()
    
    # Creates all of the outline blocks with Color.GRAY
    def initializeOutline(self):
        xSize = self.size[0] + 2
        ySize = self.size[1]
        outlineOrigin = (self.drawOrigin[0]-CONST_BlockSize, self.drawOrigin[1]+CONST_BlockSize)
        for x in range(xSize):
            block = Block(outlineOrigin, (x, 0), TileColor.GRAY)
            block2 = Block(outlineOrigin, (x, ySize+1), TileColor.GRAY)
            self.outlineBlocks.append(block)
            self.outlineBlocks.append(block2)
        for y in range(ySize):
            block = Block(outlineOrigin, (0, y + 1), TileColor.GRAY)
            block2 = Block(outlineOrigin, (xSize-1, y + 1), TileColor.GRAY)
            self.outlineBlocks.append(block)
            self.outlineBlocks.append(block2)
    
    # Draws all blocks in class
    def draw(self):
        for block in self.outlineBlocks:
            block.draw()
        for block in self.blockGrid:
            block.draw()
        for block in self.currentQueueBlocks:
            block.draw()
        if self.currentHeldObj != None:
            self.currentHeldObj.draw()
        if self.currentShape != None:
            self.currentShape.draw()
        


FPS = 30
fpsClock = pygame.time.Clock()

display = pygame.display.set_mode((CONST_ScreenSizeX, CONST_ScreenSizeY))

#tileImg = pygame.image.load('Tile.png')
#tileImg = pygame.transform.scale(tileImg, (CONST_BlockSize, CONST_BlockSize))

tileImgs = {}

# Adds given color to given surface. Does not handle negative values
def recolorTile(surface, color):
    arr = pygame.PixelArray(surface)
    for x in range(CONST_BlockSize):
        for y in range(CONST_BlockSize):
            gray = arr[x,y] % 256
            newColor = []
            newColor.append(gray + color[0])
            newColor.append(gray + color[1])
            newColor.append(gray + color[2])
            for i in range(3):
                if newColor[i] > 255:
                    newColor[i] = 255
            arr[x,y] = (newColor[0], newColor[1], newColor[2])

# Initializes TileColor array
for tC in TileColor:
    tileImg = pygame.image.load('Tile.png')
    tileImg = pygame.transform.scale(tileImg, (CONST_BlockSize, CONST_BlockSize))
    tileImgs[tC] = tileImg

# Colors all tiles
recolorTile(tileImgs[TileColor.GRAY], (0, 0, 0))
recolorTile(tileImgs[TileColor.BLUE], (0, 0, 255))
recolorTile(tileImgs[TileColor.ORANGE], (100, 35, 0))
recolorTile(tileImgs[TileColor.YELLOW], (80, 80, 0))
recolorTile(tileImgs[TileColor.TEAL], (0, 70, 70))
recolorTile(tileImgs[TileColor.RED], (255, 0, 0))
recolorTile(tileImgs[TileColor.PURPLE], (70, 0, 70))
recolorTile(tileImgs[TileColor.GREEN], (0, 255, 0))


gameWidth = (CONST_GameDimX) * CONST_BlockSize
gameHeight = (CONST_GameDimY - 2) * CONST_BlockSize

originX = (CONST_ScreenSizeX / 2) - (gameWidth / 2)
originY = (CONST_ScreenSizeY / 2) + (gameHeight / 2)

game = TetrisGameState((originX, originY), (CONST_GameDimX, CONST_GameDimY))

currentTickTime = 0
moveTicker = 0

pygame.font.init()
myFont = pygame.font.SysFont('Comic Sans Ms', 20)

CONST_PopulationSize = 50
CONST_ChampionSize = 15
currentGen = 0
highestGameScore = 0
bestGenAverage = -100
pastGenAverage = 0
#bestPlayer = None
#secondBest = None
bestPlayers = []
currentPlayers = []

class Player:
    myNetwork = None
    myGame = None
    dead = False
    fitness = 0
    
    def __init__(self, *bN):
        if len(bN) == 0:
            self.myNetwork = NrNt.NNetwork(CONST_GameDimX+2, 18, 14, 1) #Needs 4 (rotations)+ 10 (movements)outputs
        self.myGame = TetrisGameState((originX, originY), (CONST_GameDimX, CONST_GameDimY))
        
    def tick(self):
        if self.myGame.GameOver:
            self.dead = True
            self.fitness = self.myGame.getFitness()
            return
        
        inputs = self.myGame.getInputs()
        outputs = self.myNetwork.calculateNetwork(inputs)
        highest = 0
        for i in range(4):
            if outputs[i] > outputs[highest]:
                highest = i
        for i in range(highest):
            self.myGame.currentShape.rotate(1)
        highest = 4
        for i in range(4, len(outputs)):
            if outputs[i] > outputs[highest]:
                highest = i
        modified = highest - 4 - 5
        if modified == 0:
            direction = 0
        else:
            direction = modified / abs(modified)
        for i in range(abs(modified)):
            self.myGame.currentShape.move((direction,0))
        
        self.myGame.tickUntilNewShape()
    

def buildPlayers():
    global currentPlayers
    global bestPlayers
    global currentGen
    global pastGenAverage
    global bestGenAverage
    generationAverage = 0
    currentPlayers = []
    if len(bestPlayers) == 0:
        for i in range(CONST_ChampionSize):
            bestPlayers.append(Player())
    for i in range(CONST_ChampionSize):
        generationAverage += bestPlayers[i].fitness
        newP = Player(False)
        newP.myNetwork = bestPlayers[i].myNetwork.DeepCopy()
        currentPlayers.append(newP)
    #currentPlayers.append(bestPlayer)
    #currentPlayers.append(secondBest)
    
    for i in range(CONST_PopulationSize-CONST_ChampionSize):
        ch1 = int(random.uniform(0, CONST_ChampionSize))
        ch2 = int(random.uniform(0, CONST_ChampionSize))
        newP = Player(False)
        newP.myNetwork = bestPlayers[ch1].myNetwork.DeepCopy()
        newP.myNetwork.Breed(bestPlayers[ch2].myNetwork)
        newP.myNetwork.Mutate()
        currentPlayers.append(newP)
    currentGen += 1
    generationAverage /= CONST_ChampionSize
    pastGenAverage = generationAverage
    if generationAverage > bestGenAverage and generationAverage != 0:
        bestGenAverage = generationAverage
buildPlayers()

def setBestPlayer():
    global currentPlayers
    global bestPlayers
    global highestGameScore
    bestPlayers = []
    for player in currentPlayers:
        index = 0
        if player.myGame.score > highestGameScore:
            highestGameScore = player.myGame.score
        while index < len(bestPlayers):
            if player.fitness > bestPlayers[index].fitness:
                bestPlayers.insert(index, player)
                break
            index += 1
        if index == len(bestPlayers):
            bestPlayers.append(player)
        #if player.myGame.getFitness() > bestPlayer.myGame.getFitness():
        #    bestPlayer = player
    
def tickPlayers():
    global currentPlayers
    alive = False
    num = 0
    for player in currentPlayers:
        if player.dead == False:
            player.tick()
            num += 1
            alive = True
    if alive == False:
        setBestPlayer()
        buildPlayers()
    return num

#while bestPlayer.myGame.score == 0:
#    tickPlayers()

while True:
    display.fill((0,0,0))
    numAlive = tickPlayers()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                bestPlayers[0].myNetwork.print()
    '''currentTickTime += 1/FPS
    if currentTickTime > TickTime:
        currentTickTime = 0
        game.tick()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            moveTicker = 0
            if event.key == pygame.K_q:
                game.currentShape.rotate(1)
            elif event.key == pygame.K_e:
                game.currentShape.rotate(-1)
            elif event.key == pygame.K_r:
                game.hold()
            
    keys = pygame.key.get_pressed()
    pressed = False
    if keys[pygame.K_a]:
        if moveTicker == 0:
            game.currentShape.move((-1, 0))
            pressed = True
    if keys[pygame.K_d]:
        if moveTicker == 0:
            game.currentShape.move((1, 0))
            pressed = True
    if keys[pygame.K_s]:
        if moveTicker == 0:
            game.tick()
            pressed = True
    if pressed:
        moveTicker = 2
    
    if moveTicker > 0:
        moveTicker -= 1
    
    scoreText = myFont.render('Score: ' + str(game.score), False, (255,255,255))
    display.blit(scoreText,(0,0))
    
   '''
    
    for player in currentPlayers:
        if player.dead == False:
            player.myGame.draw()
            player.myGame.getHoles()
            break
    scoreText = myFont.render('Past Highest Fitness Score: ' + "{:.2f}".format(bestPlayers[0].fitness), False, (255,0,0))
    genText = myFont.render('Gen: ' + str(currentGen), False, (255,0,0))
    aliveText = myFont.render('Num Alive: ' + str(numAlive), False, (255,0,0))
    highestText = myFont.render('Highest Game Score: ' + str(highestGameScore), False, (255,0,0))
    bestAText = myFont.render('Best AvgEGS: ' + "{:.2f}".format(bestGenAverage), False, (255,0,0))
    pastAText = myFont.render('Past AvgEGS: ' + "{:.2f}".format(pastGenAverage), False, (255,0,0))
    display.blit(highestText,(0,0))
    display.blit(scoreText,(0,15))
    display.blit(bestAText,(0,30))
    display.blit(pastAText,(0,45))
    display.blit(genText,(0,60))
    display.blit(aliveText,(0,75))
    # AvgEGS = Average Elite Generation Score
    pygame.display.update()
    fpsClock.tick(FPS)