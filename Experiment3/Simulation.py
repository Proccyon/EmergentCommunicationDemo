
#-----Imports-----#
import matplotlib.colors
import numpy as np
import pyglet
from pyglet import shapes
import time
import math
import matplotlib.pyplot as plt

#-----InternalImports-----#
from Agent import Agent
from Settings import Settings, Results
from Saver import save, Log
from ChunkManager import ChunkManager
from Parallelizer import runAsync
from Pathfinder import Pathfinder, selectRandomPosition
from Automata import Automata
from DrawMethods import draw, drawWalls

#-----Constants-----#

red = [204, 6, 6]
green = [6, 204, 13]
blue = [6, 19, 204]
black = [0, 0, 0]
white = [222, 221, 215]
creatureBlue = [255, 255, 255]
brown = [124, 99, 47]


class Simulation:

    def __init__(self, Lx, Ly):

        self.Lx, self.Ly = Lx, Ly
        self.colonyX = int((self.Lx - 1) / 2)
        self.colonyY = int((self.Ly - 1) / 2)

        self.creatureCount = 10

        self.creatureArray = np.empty((Lx,Ly), dtype=list)
        self.creatureList = []
        self.setupCreatureArray()

        self.hasFoodArray = np.full((Lx, Ly), False, dtype=bool)
        self.foodAmountArray = np.zeros((Lx, Ly), dtype=int)
        self.foodDensityArray = np.zeros((Lx, Ly), dtype=float)

        self.hasWallArray = np.full((Lx, Ly), True, dtype=bool)

        self.pathfinderArray = np.full((Lx, Ly), None, dtype=Pathfinder)

        self.t = 0

        self.smellRange = 5

        self.time = time.time()
        self.dtLog = Log()

        #VisualSettings
        self.creatureSize = 8
        self.sidebarLength = 300

        self.foodChunkManager = ChunkManager(self.smellRange, self.smellRange, self.Lx, self.Ly)

        self.idCounter = 0

        self.buttons = []


        self.foodPathfinderList = []

        self.generateWalls()
        self.generateFood()
        self.generateCreatures()

        self.pathfinder = self.addPathfinder(self.colonyX, self.colonyY)

        self.batch = pyglet.graphics.Batch()

        self.wallDrawings = drawWalls(self, self.batch)

        self.automata = Automata()

        self.score = 0


    def setupCreatureArray(self):

        for x in range(self.Lx):
            for y in range(self.Ly):
                self.creatureArray[x,y] = []

    def generateWalls(self):

        R = 35
        for x in range(int(self.colonyX - R)-1, int(self.colonyX + R) + 2):
            for y in range(int(self.colonyY - R)-1, int(self.colonyY + R) + 2):
                if (x - self.colonyX)**2 + (y - self.colonyY)**2 <= R**2:
                    self.hasWallArray[x,y] = False

    def generateFood(self):

        emptySpots = np.array(np.where(self.hasFoodArray == False))
        emptySpotCount = len(emptySpots[0, :])

        foodSpawnCount = 100

        filledIndices = np.random.choice(range(emptySpotCount), foodSpawnCount, False)

        for i in filledIndices:
            x, y = emptySpots[0, i], emptySpots[1, i]
            density = np.random.randint(1, 5)
            self.addFood(x, y, 200, density)

    def generateCreatures(self):

        emptySpots = np.array(np.where(self.hasWallArray == False))
        emptySpotCount = len(emptySpots[0, :])

        filledIndices = np.random.choice(range(emptySpotCount), self.creatureCount, True)

        for i in filledIndices:
            x, y = emptySpots[0, i], emptySpots[1, i]
            self.addCreature(x, y)


    def addCreature(self, x, y):

        creature = Agent(x, y, self.idCounter)
        self.creatureArray[x, y].append(creature)
        self.creatureList.append(creature)
        self.idCounter += 1


    def addFood(self, x, y, amount, density):

        self.foodAmountArray[x, y] += amount
        self.foodDensityArray[x, y] = density

        if not self.hasFoodArray[x, y]:
            self.hasFoodArray[x, y] = True
            self.foodChunkManager.add(x, y)
            foodPathfinder = self.addPathfinder(x, y)
            self.foodPathfinderList.append(foodPathfinder)

    def removeFood(self, x, y, amount):

        if not self.hasFoodArray[x, y]:
            return

        self.foodAmountArray[x, y] -= amount

        if self.foodAmountArray[x, y] <= 0:
            self.foodAmountArray[x, y] = 0
            self.foodDensityArray[x, y] = 0
            self.hasFoodArray[x, y] = False

            index = None
            for i, pathfinder in enumerate(self.foodPathfinderList):
                if pathfinder.x0 == x and pathfinder.y0 == y:
                    index = i
                    break

            if index is not None:
                del self.foodPathfinderList[index]


    def addPathfinder(self, x, y):

        if self.pathfinderArray[x, y] is not None:
            return self.pathfinderArray[x, y]

        pathfinder = Pathfinder(self, x, y)
        self.pathfinderArray[x, y] = pathfinder
        pathfinder.init()
        return pathfinder


    def creatureWalk(self):

        for creature in self.creatureList:
            creature.walk(self)


    def updateLog(self):

        newTime = time.time()
        self.dtLog.add(newTime - self.time)
        self.dtLog.finish()
        self.time = newTime

    def step(self):

        for creature in self.creatureList:
            self.automata.run(self, creature)

        self.updateLog()

        if self.runningHidden and self.t % 300 == 0:
            print(f"Simulation progress: {self.t} / {self.totalSteps}")

        self.t += 1

    def run(self):

        self.runningHidden = False
        self.window = pyglet.window.Window(self.Lx * self.creatureSize + self.sidebarLength, self.Ly * self.creatureSize)
        self.wallDrawings = drawWalls(self, self.batch)

        @self.window.event
        def on_draw():

            self.step()
            draw(self)

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

    runSim(100, 100)


    # settingsList, resultsList = runAsync(runSimHidden, 20)
    #
    # for i in range(len(settingsList)):
    #     settings, results = settingsList[i], resultsList[i]
    #     save(settings, results)













