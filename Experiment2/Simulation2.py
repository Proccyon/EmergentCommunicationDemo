
#-----Imports-----#
import matplotlib.colors
import numpy as np
import pyglet
from pyglet import shapes
import time
import math

#-----InternalImports-----#
from Networks import Network
from Buttons import Slider
from Creature import Creature
from Settings import Settings, Results
from Saver import save, Log
from ChunkManager import ChunkManager
from Parallelizer import runAsync


#-----Constants-----#

red = [204, 6, 6]
green = [6, 204, 13]
blue = [6, 19, 204]
black = [0, 0, 0]
white = [222, 221, 215]
creatureBlue = [255, 255, 255]

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


class Simulation:

    def __init__(self, Lx, Ly):

        self.Lx, self.Ly = Lx, Ly

        self.creatureArray = np.empty((Lx,Ly), dtype=Creature)
        self.creatureList = []

        self.hasFoodArray = np.full((Lx, Ly), False, dtype=bool)
        self.foodColorArray = np.zeros((Lx, Ly, 3), dtype=float)

        self.t = 0

        # CreatureSettings
        self.creatureSpawnChance = 0.05  # Creature spawn chance per tile per tick
        self.creatureInitEnergy = 100
        self.creatureOffspringEnergy = 100
        self.creatureDrainEnergy = 1
        self.creatureSmellRange = 3

        TLife = 70
        Tpoison = 50 * TLife

        # FoodSettings
        self.foodSpawnChance = 0.001  # Food spawn chance per tile per tick
        self.foodInitEnergy = 30
        self.poisonChangeRate = (2/3) * np.pi / Tpoison
        self.poisonAngle = 0
        self.poisonStd = 3
        self.poisonOffset = 0.2
        self.poisonVector = np.zeros(3)

        self.time = time.time()
        self.dtLog = Log()
        self.energyEatenLog = Log()
        self.posEnergyEatenLog = Log()
        self.negEnergyEatenLog = Log()

        self.tWalkLog = Log()

        #VisualSettings
        self.creatureSize = 8
        self.sidebarLength = 300
        self.poisonGraphHeight = 100

        #NetworkSettings
        self.memorySize = 6
        self.memoryUpdateRate = 0.1
        self.mutateStd = 0.05
        self.mutateP = 0.01
        self.memoryShareChance = 0.25
        self.memoryHiddenSizes = [10]
        self.decisionHiddenSizes = [10]

        self.foodChunkManager = ChunkManager(self.creatureSmellRange, self.creatureSmellRange, self.Lx, self.Ly)

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
        text1 = "Food appearance"
        text2 = "Hide graphics"
        color = [186, 186, 179]

        self.foodAppearanceSlider = Slider(xMax + 0.25 * L - 0.5 * sWidth, yMax - 0.5 * backgroundHeight - 0.5 * sHeight, sWidth, sHeight,
               color, text1)

        self.showGraphicsSlider = Slider(xMax + 0.75 * L - 0.5 * sWidth, yMax - 0.5 * backgroundHeight - 0.5 * sHeight, sWidth, sHeight,
               color, text2)

        self.buttons.append(self.foodAppearanceSlider)
        self.buttons.append(self.showGraphicsSlider)

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


    def addCreature(self, x, y, energy, gen, network):

        creature = Creature(energy, x, y, network, gen, self.idCounter)
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
            self.addFood(x, y, generateColor())

    def addFood(self, x, y, color):
        self.hasFoodArray[x, y] = True
        self.foodColorArray[x, y] = color
        self.foodChunkManager.add(x, y)

    def spawnCreatures(self):

        emptySpots = np.array(np.where(self.creatureArray == None))
        emptySpotCount = len(emptySpots[0,:])

        creatureSpawnCount = np.random.binomial(emptySpotCount, self.creatureSpawnChance)

        filledIndices = np.random.choice(range(emptySpotCount), creatureSpawnCount, False)

        for i in filledIndices:
            x, y = emptySpots[0, i], emptySpots[1, i]

            network = Network(self.memorySize, self.memoryUpdateRate, self.mutateStd, self.mutateP, self.memoryHiddenSizes, self.decisionHiddenSizes)
            self.addCreature(x, y, self.creatureInitEnergy, 0, network)

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

    def updateLog(self):

        self.energyEatenLog.finish()
        self.posEnergyEatenLog.finish()
        self.negEnergyEatenLog.finish()

        newTime = time.time()
        self.dtLog.add(newTime - self.time)
        self.dtLog.finish()
        self.time = newTime

    def step(self):

        t0 = time.time()
        self.creatureWalk()
        t1 = time.time()
        self.creatureFeeding()
        t2 = time.time()
        self.creatureEnergyDrain()
        t3 = time.time()
        self.creatureReplicate()
        t4 = time.time()
        self.updatePoison()
        t5 = time.time()
        self.spawnFood()
        t6 = time.time()

        dt1, dt2, dt3, dt4, dt5, dt6 = t1-t0,t2-t1,t3-t2,t4-t3,t5-t4, t6-t5
        T = dt1+dt2+dt3+dt4+dt5+dt6

        self.tWalkLog.add(dt1)
        self.tWalkLog.finish()

        # if T > 0 and self.t % 300 == 0:
        #     print(f"walk: {round(dt1,4)}({round(100*dt1/T,1)}%)")
        #     print(f"feeding: {round(dt2,4)}({round(100*dt2/T, 1)})%")
        #     print(f"EnergyDrain: {round(dt3,4)}({round(100*dt3/T, 1)})%")
        #     print(f"Replicate: {round(dt4,4)}({round(100*dt4/T, 1)})%")
        #     print(f"updatePoison: {round(dt5,4)}({round(100*dt5/T, 1)})%")
        #     print(f"SpawnFood: {round(dt6, 4)}({round(100 * dt6 / T, 1)})%")
        #
        #     print(f"Walk average: {round(self.tWalkLog.pastAverage(300),4)}")

        creaturesToDestroy = []

        for creature in self.creatureList:
            if creature.energy <= 0 or creature.toBeDestroyed:
                creaturesToDestroy.append(creature)

        for creature in creaturesToDestroy:
            creature.destroy(self)

        self.updateLog()

        if self.runningHidden and self.t % 300 == 0:
            print(f"Simulation progress: {self.t} / {self.totalSteps}")

        # if self.t % 50 == 0:
        #     gens = [creature.gen for creature in self.creatureList]
        #     genAvg = np.average(gens)
        #     genMin = np.amin(gens)
        #     genMax = np.amax(gens)
        #     print(f"Average lifetime: {self.t / genAvg}")
        #     print(f"genAvg: {genAvg}")
        #     print(f"genMin-genMax: {genMin}-{genMax}")


        self.t += 1


    def drawFPS(self, batch):

        yMax = self.Ly * self.creatureSize

        fps = 1 / self.dtLog.pastAverage(3)

        text = str(np.round(fps, 2)) + "FPS"

        textDrawing = pyglet.text.Label(text, x=0, y=yMax-15, batch=batch, color=[235, 231, 16, 255])
        return textDrawing


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
        color = creatureBlue
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
        L = self.sidebarLength
        background = shapes.Rectangle(xMax, 0, L, yMax, color=white, batch=batch)
        return background

    # Draws graph on the right showing energy values for different food colors
    def drawPoisonGraph(self, batch):

        xMax = self.Lx * self.creatureSize
        yMax = self.Ly * self.creatureSize
        L = self.sidebarLength

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

    def drawEatingGraph(self, batch):

        L = self.sidebarLength
        xMax = self.Lx * self.creatureSize
        yMax = self.Ly * self.creatureSize - 2 * L

        colors = [red, green]

        window = 150

        pPos = self.posEnergyEatenLog.pastAverage(window)#np.average(self.posEnergyEatenLog[nMin:n])
        pNeg = self.negEnergyEatenLog.pastAverage(window)
        pList = [pNeg, pPos]

        xMid = xMax + 0.5 * L
        yMid = yMax - 0.5 * L
        barWidth = 0.2 * L
        gapWidth = 0.1 * L
        barMaxHeight = 0.4 * L
        dividerHeight = 0.004 * L
        yText = yMid + 0.4 * L
        yTitle = yMid - 0.06 * L

        titles = ["p(eat|dE<0)", "p(eat|dE>0)"]

        barDrawings = []

        for i in range(2):
            color = colors[i]

            xBar = xMid + (i - 0.5) * (barWidth + gapWidth) - 0.5 * barWidth

            barHeight = barMaxHeight * pList[i]

            barDrawing = shapes.Rectangle(xBar, yMid, barWidth, barHeight, color=color, batch=batch)
            dividerDrawing = shapes.Rectangle(xBar, yMid- 0.5 * dividerHeight, barWidth, dividerHeight, color=black, batch=batch)

            xText = xBar + 0.5 * barWidth
            text = str(np.round(pList[i],2))
            textDrawing = pyglet.text.Label(text, x=xText, y=yText, batch=batch, anchor_x='center', color=[0,0,0,255])
            titleDrawing = pyglet.text.Label(titles[i], x=xText, y=yTitle, batch=batch, anchor_x='center',
                                            color=[0, 0, 0, 255])

            barDrawings.append(barDrawing)
            barDrawings.append(dividerDrawing)
            barDrawings.append(textDrawing)
            barDrawings.append(titleDrawing)

        return barDrawings


    def draw(self):

        self.window.clear()

        batch = pyglet.graphics.Batch()

        if not self.showGraphicsSlider.on:
            foodDrawings = self.drawFood(batch)
            creatureDrawings = self.drawCreatures(batch)


        sidebar = self.drawSidebar(batch)
        poisonGraphDrawings = self.drawPoisonGraph(batch)
        eatingGraphsDrawings = self.drawEatingGraph(batch)
        fps = self.drawFPS(batch)

        buttonDrawings = []
        for button in self.buttons:
            buttonDrawings.append(button.draw(batch))

        batch.draw()

    def run(self):

        self.runningHidden = False
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

        self.window.close()

    def runHidden(self, steps):

        self.runningHidden = True
        self.totalSteps = steps
        self.settings = Settings(self)

        for _ in range(steps):
            self.step()

        results = Results(self)

        return self.settings, results

        #save(self.settings, results)



# def runSimHidden(Lx, Ly, steps):
#     sim = Simulation(Lx, Ly)
#     return sim.runHidden(steps)

def runSimHidden(id):
    sim = Simulation(100, 100)
    return sim.runHidden(50000)

def runSim(Lx, Ly):
    sim = Simulation(Lx, Ly)
    sim.run()


if __name__ == "__main__":

    # runSim(100, 100)


    settingsList, resultsList = runAsync(runSimHidden, 20)

    for i in range(len(settingsList)):
        settings, results = settingsList[i], resultsList[i]
        save(settings, results)













