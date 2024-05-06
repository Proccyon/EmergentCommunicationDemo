import matplotlib.colors
#-----Imports-----#
import numpy as np
import pyglet
from pyglet import shapes
import time
import matplotlib.pyplot as plt

# Randomly generates a 3d vector where elements sum to 1 and el > 0, el < 1
def generateColor():

    Cx = np.array([1/np.sqrt(2), 0, -1/np.sqrt(2)])
    Cy = np.array([1/np.sqrt(6), -np.sqrt(2/3), 1/np.sqrt(6)])
    C0 = np.array([1/3, 1/3, 1/3])

    while True:

        a = np.random.uniform(-0.85,0.75)
        b = np.random.uniform(-0.85, 0.45)

        C = a * Cx + b * Cy + C0

        if C[0] > 0 and C[0] < 1 and C[1] > 0 and C[1] < 1 and C[2] > 0 and C[2] < 1:
            return C


class Slider:

    def __init__(self, x, y, width, height, color, text):

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.on = False
        self.text = text


    def draw(self, batch):

        R = 0.5 * self.height
        Bh = self.height
        Bw = self.width - self.height

        xC1 = self.x+R
        xC2 = self.x+R+Bw
        yC = self.y+R

        #Draw background
        c1 = shapes.Circle(xC1, yC, R, color=self.color,
                      batch=batch)
        b = shapes.Rectangle(self.x+R, self.y, Bw, Bh, color=self.color, batch=batch)
        c2 = shapes.Circle(xC2, yC, R, color=self.color,
                      batch=batch)

        xText = self.x + 0.5 * self.width
        yText = self.y + self.height + 0.5 * self.height

        textDrawing = pyglet.text.Label(self.text, x=xText, y=yText, batch=batch, anchor_x='center', anchor_y='center', color=[0, 0, 0, 255])

        if self.on:
            xDot = xC2
        else:
            xDot = xC1

        cDot = shapes.Circle(xDot, yC, 0.8 * R, color=[0,0,0,255],
                      batch=batch)

        return [c1, b, c2, cDot, textDrawing]

    def isClicked(self, x, y):
        return (self.x < x < self.x + self.width and
                self.y < y < self.y + self.height)

    def onClick(self, sim):
        self.on = not self.on

class Creature:

    def __init__(self, energy, x, y, id):

        self.energy = energy
        self.x = x
        self.y = y
        self.id = id
        self.toBeDestroyed = False

    def destroy(self, sim):

        sim.creatureArray[self.x,self.y] = None

        placement = 0
        for i, creature in enumerate(sim.creatureList):
            if self.id == creature.id:
                placement = i
                break

        del sim.creatureList[placement]


    def move(self, xNew, yNew, sim):

        if xNew < 0 or yNew < 0 or xNew >= sim.Lx or yNew >= sim.Ly:
            return

        if sim.creatureArray[xNew, yNew] != None:
            return

        sim.creatureArray[self.x, self.y] = None

        self.x = xNew
        self.y = yNew

        sim.creatureArray[xNew, yNew] = self

    def eat(self, sim):

        if sim.hasFoodArray[self.x, self.y]:

            dE = sim.getFoodEnergy(sim.foodColorArray[self.x, self.y])

            self.energy += dE
            sim.hasFoodArray[self.x, self.y] = False


    def walk(self, sim):

        freeDirections = self.getFreeDirections(sim)
        if sim.hasFoodArray[self.x, self.y]or len(freeDirections) == 0:
            return

        r = sim.creatureSmellRange
        xmin, xmax = max(0, self.x - r), min(sim.Lx-1, self.x + r + 1)
        ymin, ymax = max(0, self.y - r), min(sim.Ly-1, self.y + r + 1)

        foods = sim.hasFoodArray

        sUp = np.sum(foods[xmin:xmax, self.y+1:ymax])
        sDown = np.sum(foods[xmin:xmax, ymin:self.y])
        sRight = np.sum(foods[self.x+1:xmax, ymin:ymax])
        sLeft = np.sum(foods[xmin:self.x, ymin:ymax])

        foodValues = np.array([sUp, sDown, sRight, sLeft])

        directions = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        if np.sum(foodValues) == 0:
            dp = freeDirections[np.random.randint(len(freeDirections))]
        else:
            maxDirections = directions[foodValues == np.amax(foodValues)]
            dp = np.array(maxDirections[np.random.randint(len(maxDirections))])

        self.move(self.x+dp[0], self.y+dp[1], sim)


    def replicate(self, sim):

        if self.energy < sim.creatureOffspringEnergy:
            return

        directions = self.getFreeDirections(sim)

        if len(directions) == 0:
            return

        direction = directions[np.random.randint(len(directions))]

        xChild, yChild = self.x+direction[0], self.y+direction[1]
        childEnergy = self.energy / 2
        sim.addCreature(xChild, yChild, childEnergy)
        self.energy = childEnergy

    def getFreeDirections(self, sim):

        directions = []
        if self.x > 0 and sim.creatureArray[self.x-1, self.y] == None:
            directions.append([-1,0])
        if self.x < sim.Lx-1 and sim.creatureArray[self.x+1, self.y] == None:
            directions.append([1,0])
        if self.y > 0 and sim.creatureArray[self.x, self.y-1] == None:
            directions.append([0,-1])
        if self.y < sim.Ly-1 and sim.creatureArray[self.x, self.y+1] == None:
            directions.append([0,1])

        return directions

    def getOccupiedDirections(self, sim):

        directions = []
        if self.x > 0 and sim.creatureArray[self.x-1, self.y] != None:
            directions.append([-1,0])
        if self.x < sim.Lx-1 and sim.creatureArray[self.x+1, self.y] != None:
            directions.append([1,0])
        if self.y > 0 and sim.creatureArray[self.x, self.y-1] != None:
            directions.append([0,-1])
        if self.y < sim.Ly-1 and sim.creatureArray[self.x, self.y+1] != None:
            directions.append([0,1])

        return directions



class Simulation:


    def __init__(self, Lx, Ly):

        self.Lx, self.Ly = Lx, Ly

        self.creatureArray = np.empty((Lx,Ly), dtype=Creature)
        self.creatureList = []

        self.hasFoodArray = np.full((Lx, Ly), False, dtype=bool)
        self.foodColorArray = np.zeros((Lx, Ly, 3), dtype=float)

        # CreatureSettings
        self.creatureSpawnChance = 0.05  # Creature spawn chance per tile per tick
        self.creatureInitEnergy = 100
        self.creatureOffspringEnergy = 200
        self.creatureDrainEnergy = 1
        self.creatureSmellRange = 3

        # FoodSettings
        self.foodSpawnChance = 0.001  # Food spawn chance per tile per tick
        self.foodInitEnergy = 50
        self.poisonChangeRate = 0.001
        self.poisonAngle = 0
        self.poisonStd = 1
        self.poisonOffset = 0.3
        self.poisonVector = np.zeros(3)

        #VisualSettings
        self.creatureSize = 8
        self.sidebarLength = 300
        self.poisonGraphHeight = 100

        self.idCounter = 0

        self.buttons = []

        self.setButtons()

        self.spawnCreatures()

    def setButtons(self):

        xMax = self.Lx * self.creatureSize
        yMax = self.Ly * self.creatureSize - self.sidebarLength
        L = self.sidebarLength
        backgroundHeight = 0.5 * L

        sWidth = 0.3 * L
        sHeight = 0.1 * L
        text = "Food appearance"
        color = [186, 186, 179]

        slider = Slider(xMax + 0.5 * L - 0.5 * sWidth, yMax - 0.5 * backgroundHeight - 0.5 * sHeight, sWidth, sHeight,
               color, text)

        self.foodAppearanceSlider = slider

        self.buttons.append(slider)

    def getPoisonVector(self):

        Cx = np.array([1 / np.sqrt(2), 0, -1 / np.sqrt(2)])
        Cy = np.array([1 / np.sqrt(6), -np.sqrt(2 / 3), 1 / np.sqrt(6)])
        C0 = self.poisonOffset * np.array([1,1,1])

        self.poisonVector = 3 * (self.poisonStd**2) * (np.cos(self.poisonAngle) * Cx + np.sin(self.poisonAngle) * Cy) + C0

    def getFoodEnergy(self, C):
        return self.foodInitEnergy * np.dot(C, self.poisonVector)

    def updatePoison(self):

        self.poisonAngle += self.poisonChangeRate
        self.getPoisonVector()


    def addCreature(self, x, y, energy):

        creature = Creature(energy, x, y, self.idCounter)
        self.creatureArray[x, y] = creature
        self.creatureList.append(creature)
        self.idCounter += 1

    def spawnFood(self):

        emptySpots = np.array(np.where(self.hasFoodArray == False))
        emptySpotCount = len(emptySpots[0, :])

        foodSpawnCount = np.random.binomial(emptySpotCount, self.foodSpawnChance)

        filledIndices = np.random.choice(range(emptySpotCount), foodSpawnCount, False)

        for i in filledIndices:
            x, y = emptySpots[0, i], emptySpots[1, i]
            self.hasFoodArray[x, y] = True
            self.foodColorArray[x, y] = generateColor()


    def spawnCreatures(self):

        emptySpots = np.array(np.where(self.creatureArray == None))
        emptySpotCount = len(emptySpots[0,:])

        creatureSpawnCount = np.random.binomial(emptySpotCount, self.creatureSpawnChance)

        filledIndices = np.random.choice(range(emptySpotCount), creatureSpawnCount, False)

        for i in filledIndices:
            x, y = emptySpots[0, i], emptySpots[1, i]

            self.addCreature(x, y, self.creatureInitEnergy)

    def creatureFeeding(self):

        for creature in self.creatureList:
            creature.eat(self)

    def creatureEnergyDrain(self):

        for creature in self.creatureList:
            creature.energy -= self.creatureDrainEnergy

    def creatureWalk(self):

        for creature in self.creatureList:
            creature.walk(self)

    def creatureReplicate(self):

        for creature in self.creatureList:
            creature.replicate(self)

    def step(self):

        self.spawnFood()

        self.creatureWalk()
        self.creatureFeeding()
        self.creatureEnergyDrain()
        self.creatureReplicate()
        self.updatePoison()

        creaturesToDestroy = []

        for creature in self.creatureList:
            if creature.energy <= 0 or creature.toBeDestroyed:
                creaturesToDestroy.append(creature)

        for creature in creaturesToDestroy:
            creature.destroy(self)


    def drawFood(self, batch):


        size = self.creatureSize

        foodDrawings = []
        for x in range(self.Lx):
            for y in range(self.Ly):

                if not self.hasFoodArray[x, y]:
                    continue

                if self.foodAppearanceSlider.on:
                    cFood = (50, 225, 30)
                    cPoison = (255, 0, 0)

                    sFood = self.getFoodEnergy(self.foodColorArray[x, y]) / (3 * self.foodInitEnergy * self.poisonStd**2)
                    if sFood > 1:
                        sFood = 1
                    if sFood < -1:
                        sFood = -1

                    if sFood > 0:
                        color = [int(sFood * cFood[i]) for i in range(len(cFood))]
                    else:
                        color = [int(-sFood * cPoison[i]) for i in range(len(cPoison))]

                    foodDrawing = shapes.Rectangle(size * x, size * y, size, size, color=color, batch=batch)
                    foodDrawings.append(foodDrawing)

                else:

                    color = [int(c * 255) for c in self.foodColorArray[x, y]]

                    foodDrawing = shapes.Rectangle(size * x, size * y, size, size, color=color, batch=batch)
                    foodDrawings.append(foodDrawing)




        return foodDrawings

    def drawCreatures(self, batch):

        creatureDrawings = []
        color = [55,55,255]
        size = self.creatureSize

        for creature in self.creatureList:
            s = min(1, creature.energy / self.creatureInitEnergy)
            s = max(0.5, s)

            creatureColor = [int(s * color[i]) for i in range(len(color))]
            creatureDrawing = shapes.Circle(size * (creature.x+0.5), size * (creature.y+0.5), 0.5*size, color=creatureColor, batch=batch)

            creatureDrawings.append(creatureDrawing)

        return creatureDrawings

    def drawSidebar(self, batch):

        xMax = self.Lx * self.creatureSize
        yMax = self.Ly * self.creatureSize
        white = [222, 221, 215]
        L = self.sidebarLength
        background = shapes.Rectangle(xMax, 0, L, yMax, color=white, batch=batch)
        return background

    # Draws graph on the right showing energy values for different food colors
    def drawPoisonGraph(self, batch):

        xMax = self.Lx * self.creatureSize
        yMax = self.Ly * self.creatureSize
        L = self.sidebarLength

        red = [204,6,6]
        green = [6, 204, 13]
        blue = [6, 19, 204]
        black = [0, 0, 0]
        barColors = [red, green, blue]

        pMax = max(0, 3 * (self.poisonStd**2) + self.poisonOffset)
        pMin = min(0, 3 * (self.poisonStd**2) - self.poisonOffset)
        dp = pMax - pMin

        barDrawings = []

        xMid = xMax + 0.5 * L
        yMid = yMax - 0.5 * L
        barWidth = 0.2 * L
        gapWidth = 0.1 * L
        barMaxHeight = 0.4 * L
        dividerHeight = 0.004 * L
        yText = yMid + 0.4 * L

        for i in range(3):
            color = barColors[i]

            xBar = xMid + (1 - i) * (barWidth + gapWidth) - 0.5 * barWidth
            pNorm = self.poisonVector[i] / dp
            barHeight = barMaxHeight * pNorm

            barDrawing = shapes.Rectangle(xBar, yMid, barWidth, barHeight, color=color, batch=batch)
            dividerDrawing = shapes.Rectangle(xBar, yMid- 0.5 * dividerHeight, barWidth, dividerHeight, color=black, batch=batch)

            xText = xBar + 0.5 * barWidth
            text = str(np.round(pNorm,2))
            textDrawing = pyglet.text.Label(text, x=xText, y=yText, batch=batch, anchor_x='center', color=[0,0,0,255])

            barDrawings.append(barDrawing)
            barDrawings.append(dividerDrawing)
            barDrawings.append(textDrawing)

        return barDrawings

    def draw(self):

        self.window.clear()

        batch = pyglet.graphics.Batch()

        foodDrawings = self.drawFood(batch)
        sidebar = self.drawSidebar(batch)
        creatureDrawings = self.drawCreatures(batch)
        poisonGraphDrawings = self.drawPoisonGraph(batch)
        #settingDrawings = self.drawVisualSettings(batch)

        buttonDrawings = []
        for button in self.buttons:
            buttonDrawings.append(button.draw(batch))

        batch.draw()

    def run(self, drawGame=True):

        if (drawGame):

            self.window = pyglet.window.Window(self.Lx * self.creatureSize + self.sidebarLength, self.Ly * self.creatureSize)

            @self.window.event
            def on_draw():

                self.step()
                self.draw()

            @self.window.event
            def on_mouse_press(x, y, key, modifiers):
                if key == pyglet.window.mouse.LEFT:

                    for button in self.buttons:
                        if button.isClicked(x, y):
                            button.onClick(self)

            pyglet.app.run()

        if (drawGame):
            self.window.close()



sim = Simulation(100, 100)

sim.run()

