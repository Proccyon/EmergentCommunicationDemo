
#-----Imports-----#
import matplotlib.colors
import numpy as np
import pyglet
import time
import math

#-----InternalImports-----#
from Agent import Agent
from Settings import Settings, Results
from Saver import save, Log
from ChunkManager import ChunkManager
from BaseClasses import Brain
from Automata import Automata
from BehaviourTree import BehaviourTree
from DrawMethods import draw, drawWalls
from Map import *
#from Plotter import readResults


class SimSettings:

    def __init__(self, smellRange, commRange):
        self.smellRange = smellRange
        self.commRange = commRange

    def toString(self):
        return (f"smellRange = {self.smellRange}"
                f"commRange = {self.commRange}")

class Simulation:

    def __init__(self, map: Map, brain: Brain, simSettings: SimSettings):

        self.smellRange = simSettings.smellRange
        self.commRange = simSettings.commRange

        self.agentList = []
        self.foodPosList = []
        self.foodWithinRangeArray = np.full((map.Lx, map.Ly), -1, dtype=int)
        self.idCounter = 0
        self.t = 0
        self.score = 0
        self.scoreList = []
        self.bestGatheredDensity = 0
        self.foodCollected = 0

        self.time = time.time()
        self.dtLog = Log()

        #VisualSettings
        self.creatureSize = int(8 * (100 / max(map.Lx, map.Ly)))
        self.sidebarLength = 300

        self.initMap(map)

        self.buttons = []

        self.batch = pyglet.graphics.Batch()

        self.wallDrawings = drawWalls(self, self.batch)

        self.brain = brain

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

        self.foodChunkManager = ChunkManager(self.smellRange, self.smellRange, self.Lx, self.Ly)

        for x in range(self.Lx):
            for y in range(self.Ly):
                self.creatureArray[x, y] = []
                for _ in range(map.creatureAmountArray[x, y]):
                    self.addCreature(x, y)

                if map.foodAmountArray[x, y] > 0:
                    self.foodPosList.append((x, y))
                    self.hasFoodArray[x, y] = True
                    self.foodChunkManager.add(x, y)


    def addCreature(self, x, y):

        creature = Agent(x, y, self.idCounter)
        self.creatureArray[x, y].append(creature)
        self.agentList.append(creature)
        self.idCounter += 1

    def getPathfinder(self, x, y):
        return self.map.pathfinderArray[x, y]

    def isValidPosition(self, x, y):
        return x >= 0 and y >= 0 and x < self.Lx and y < self.Ly and not self.hasWallArray[x, y]

    def removeFood(self, x, y, amount):

        if not self.hasFoodArray[x, y]:
            return

        self.foodAmountArray[x, y] -= amount

        if self.foodAmountArray[x, y] <= 0:
            self.foodAmountArray[x, y] = 0
            self.foodDensityArray[x, y] = 0
            self.hasFoodArray[x, y] = False
            self.foodChunkManager.remove(x, y)

            index = None
            for i, pos in enumerate(self.foodPosList):
                xFood, yFood = pos
                if xFood == x and yFood == y:
                    index = i
                    break

            if index is not None:
                del self.foodPosList[index]


    def agentWalk(self):

        for agent in self.agentList:
            agent.walk(self)

    def updateLog(self):

        newTime = time.time()
        self.dtLog.add(newTime - self.time)
        self.dtLog.finish()
        self.time = newTime

    def step(self):

        for agent in self.agentList:
            agent.resetTarget(self)
            self.brain.run(self, agent)

        self.scoreList.append(self.score)
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

        return np.array([self.score, np.average(self.scoreList), self.bestGatheredDensity, self.foodCollected])


def runSimHidden(id, map, brain, simSettings, tMax):
    sim = Simulation(map, brain, simSettings)
    return id, sim.runHidden(tMax)

def runSim(map, brain, simSettings):
    sim = Simulation(map, brain, simSettings)
    sim.run()


if __name__ == "__main__":


    # settingsArray, resultsArray = readResults()
    # results = resultsArray[3][0]
    #
    # i = len(results.scoreArray)-1
    # jMax = np.argmax(results.scoreArray[i, :])
    # bestAutomata = results.automataArray[i, jMax]

    automata = Automata().initBaseAutomata()
    behaviourTree = BehaviourTree().initCommunicatingAgent()

    simSettings = SimSettings(5, 2)
    mapSettings = FourRoomsMapSettings(6, 6, 6, 1, 30, 300, 1, 2, 4, 8)
    map = FourRoomsMap(mapSettings).init()
    # mapSettings = CircleMapSettings(16,30, 10, [1,1], 500)
    # map = CircleMap(mapSettings).init()

    t0 = time.time()
    runSimHidden(0, map, behaviourTree, simSettings, 1000)
    print(time.time() - t0)


    #runSim(map, behaviourTree, simSettings)


















