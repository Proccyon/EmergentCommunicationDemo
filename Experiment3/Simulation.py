
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
from Map import Map, CircleMap, FourRoomsMap

#-----Constants-----#

red = [204, 6, 6]
green = [6, 204, 13]
blue = [6, 19, 204]
black = [0, 0, 0]
white = [222, 221, 215]
creatureBlue = [255, 255, 255]
brown = [124, 99, 47]


class SimSettings:

    def __init__(self):
        self.smellRange = 5


class Simulation:

    def __init__(self, map, automata):

        self.creatureList = []
        self.foodPosList = []
        self.idCounter = 0
        self.t = 0
        self.smellRange = 5
        self.score = 0

        self.time = time.time()
        self.dtLog = Log()

        #VisualSettings
        self.creatureSize = 8
        self.sidebarLength = 300

        self.initMap(map)

        self.buttons = []

        self.batch = pyglet.graphics.Batch()

        self.wallDrawings = drawWalls(self, self.batch)

        self.automata = automata


    def initMap(self, map):

        self.map = map
        self.colonyX, self.colonyY = map.colonyX, map.colonyY
        self.creatureCount = map.creatureCount
        self.Lx, self.Ly = map.Lx, map.Ly

        self.creatureArray = np.empty((self.Lx,self.Ly), dtype=list)
        self.hasFoodArray = np.full((self.Lx, self.Ly), False, dtype=bool)

        self.hasWallArray = map.hasWallArray.copy()
        self.foodDensityArray = map.foodDensityArray.copy()
        self.foodAmountArray = map.foodAmountArray.copy()

        for x in range(self.Lx):
            for y in range(self.Ly):
                self.creatureArray[x, y] = []
                for _ in range(map.creatureAmountArray[x, y]):
                    self.addCreature(x, y)

                if map.foodAmountArray[x, y] > 0:
                    self.foodPosList.append((x, y))
                    self.hasFoodArray[x, y] = True


    def addCreature(self, x, y):

        creature = Agent(x, y, self.idCounter)
        self.creatureArray[x, y].append(creature)
        self.creatureList.append(creature)
        self.idCounter += 1

    def getPathfinder(self, x, y):
        return self.map.pathfinderArray[x, y]

    def removeFood(self, x, y, amount):

        if not self.hasFoodArray[x, y]:
            return

        self.foodAmountArray[x, y] -= amount

        if self.foodAmountArray[x, y] <= 0:
            self.foodAmountArray[x, y] = 0
            self.foodDensityArray[x, y] = 0
            self.hasFoodArray[x, y] = False

            index = None
            for i, pos in enumerate(self.foodPosList):
                xFood, yFood = pos
                if xFood== x and yFood == y:
                    index = i
                    break

            if index is not None:
                del self.foodPosList[index]


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

        # if self.runningHidden and self.t % 300 == 0:
        #     print(f"Simulation progress: {self.t} / {self.totalSteps}")

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

        for _ in range(steps):
            self.step()

        return self.score




# def runSimHidden(Lx, Ly, steps):
#     sim = Simulation(Lx, Ly)
#     return sim.runHidden(steps)

def runSimHidden(id, map, automata, tMax):
    sim = Simulation(map, automata)
    return sim.runHidden(tMax)

def runSim(map, automata):
    sim = Simulation(map, automata)
    sim.run()


if __name__ == "__main__":

    #map = CircleMap(20, 50, 10, (0, 5),34)
    map = FourRoomsMap(12,6,6,1,15,10,1,2,3,4)
    automata = Automata().initBaseAutomata()
    map.init()
    runSim(map, automata)


    # settingsList, resultsList = runAsync(runSimHidden, 20)
    #
    # for i in range(len(settingsList)):
    #     settings, results = settingsList[i], resultsList[i]
    #     save(settings, results)













