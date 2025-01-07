
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
from DrawMethods import draw, drawStatic
from Map import *
#from Plotter import readResults
from Parallelizer import runAsync


class SimSettings:

    def __init__(self, smellRange:int, commRange:int, nComm:float, pDistortFloat:float=0, stdDistortFloat:float=0, pDistortCoord:float=0, stdDistortCoord:float=0):
        self.smellRange = smellRange
        self.commRange = commRange
        self.nComm = nComm
        self.pDistortFloat = pDistortFloat
        self.stdDistortFloat = stdDistortFloat
        self.pDistortCoord = pDistortCoord
        self.stdDistortCoord = stdDistortCoord

    def toString(self):
        return (f"smellRange = {self.smellRange}"
                f"commRange = {self.commRange}"
                f"nComm = {self.nComm}"
                f"pDistortFloat = {self.pDistortFloat}"
                f"stdDistortFloat = {self.stdDistortFloat}"
                f"pDistortCoord = {self.pDistortCoord}"
                f"stdDistortCoord = {self.stdDistortCoord}")

class Simulation:

    def __init__(self, map: Map, brain: Brain, simSettings: SimSettings, pathfinder: Pathfinder):

        self.pathfinder = pathfinder
        self.smellRange = simSettings.smellRange
        self.commRange = simSettings.commRange
        self.nComm = simSettings.nComm
        self.pDistortFloat = simSettings.pDistortFloat
        self.stdDistortFloat = simSettings.stdDistortFloat
        self.pDistortCoord = simSettings.pDistortCoord
        self.stdDistortCoord = simSettings.stdDistortCoord

        self.agentList = []
        self.foodPosList = []
        self.foodWithinRangeArray = np.full((map.Lx, map.Ly), -1, dtype=int)
        self.idCounter = 0
        self.t = 0
        self.score = 0
        self.scoreList = []
        self.foodCollectedList = []
        self.bestGatheredDensity = 0
        self.foodCollected = 0
        self.avgAgentCenterDistanceList = []
        self.avgWaypointCenterDistanceList = []
        self.avgWaypointAgentDistanceList = []

        self.time = time.time()
        self.dtLog = Log()

        #VisualSettings
        self.creatureSize = int(8 * (100 / max(map.Lx, map.Ly)))
        self.sidebarLength = 300

        self.initMap(map)

        self.buttons = []

        self.batch = pyglet.graphics.Batch()

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

    def getDistance(self, x0, y0, x, y):
        return self.pathfinder.getDistance(x0, y0, x, y)



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

    def updateLog(self):

        newTime = time.time()
        self.dtLog.add(newTime - self.time)
        self.dtLog.finish()
        self.time = newTime

    def logDistances(self):

        agentCenterDistanceList = []
        waypointCenterDistanceList = []
        waypointAgentDistanceList = []
        for agent in self.agentList:
            agentCenterDistance = self.pathfinder.getDistance(agent.x, agent.y, self.colonyX, self.colonyY)
            agentCenterDistanceList.append(agentCenterDistance)

            xWaypoint, yWaypoint = agent.coordsArray[0]
            if xWaypoint >= 0 or yWaypoint >= 0:
                waypointCenterDistance = self.pathfinder.getDistance(xWaypoint, yWaypoint, self.colonyX, self.colonyY)
                waypointAgentDistance = self.pathfinder.getDistance(xWaypoint, yWaypoint, agent.x, agent.y)
                waypointCenterDistanceList.append(waypointCenterDistance)
                waypointAgentDistanceList.append(waypointAgentDistance)

        self.avgAgentCenterDistanceList.append(np.average(agentCenterDistanceList))

        if len(waypointCenterDistanceList) > 0:
            self.avgWaypointCenterDistanceList.append(np.average(waypointCenterDistanceList))
            self.avgWaypointAgentDistanceList.append(np.average(waypointAgentDistanceList))
        else:
            self.avgWaypointCenterDistanceList.append(-1)
            self.avgWaypointAgentDistanceList.append(-1)


    def determineIfAntMill(self, minFoodIncrease=0.15, minWaypointDistance=0.8):

        def averageBackwards(xList, n):
            xAveraged = np.zeros(xList.shape)
            for i in range(len(xList)):
                iMin = max(0, i - n + 1)
                xAveraged[i] = np.average(xList[iMin:i + 1])

            return xAveraged

        def diff(xList):
            xDiff = np.diff(xList)
            return np.insert(xDiff, 0, 0)

        R = self.map.r1 + self.map.d
        walkDistance = 2 * R + 1
        nAverage = walkDistance

        foodCollectedArray = averageBackwards(np.array(self.foodCollectedList), nAverage) * nAverage
        foodIncreaseArray = diff(foodCollectedArray) / (nAverage * len(self.agentList) / walkDistance)
        waypointDistance = self.avgWaypointCenterDistanceList[-1] / R

        foodConstraint = foodIncreaseArray[-1] < minFoodIncrease
        waypointConstraint = (waypointDistance < minWaypointDistance) * (waypointDistance >= 0)

        isAntMill = foodConstraint * waypointConstraint

        return isAntMill, foodConstraint, waypointConstraint


    def step(self):

        # time.sleep(0.1)
        for agent in self.agentList:
            agent.resetTarget(self)
            agent.nearbyAgentList = None
            self.brain.run(self, agent)

        self.logDistances()

        self.scoreList.append(self.score)
        self.foodCollectedList.append(self.foodCollected)
        self.updateLog()

        # if self.runningHidden and self.t % 300 == 0:
        #     print(f"Simulation progress: {self.t} / {self.totalSteps}")

        #print(np.amax([agent.floatArray[0] for agent in self.agentList]))

        self.t += 1

    def run(self):

        self.runningHidden = False
        self.window = pyglet.window.Window(self.Lx * self.creatureSize + self.sidebarLength, self.Ly * self.creatureSize)
        self.staticDrawings = drawStatic(self)

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

        return np.array([self.score, np.average(self.scoreList), self.bestGatheredDensity, self.foodCollected,
                         self.avgAgentCenterDistanceList, self.avgWaypointCenterDistanceList, self.avgWaypointAgentDistanceList, self.scoreList, self.foodCollectedList], dtype=object)


def runSimHidden(id, map, brain, simSettings, tMax):
    pathfinder = Pathfinder(map).init()

    sim = Simulation(map, brain, simSettings, pathfinder)
    return id, sim.runHidden(tMax)

def runSim(map, brain, simSettings, pathfinder):
    sim = Simulation(map, brain, simSettings, pathfinder)
    sim.run()


if __name__ == "__main__":

    # settingsArray, resultsArray = readResults()
    # results = resultsArray[3][0]
    #
    # i = len(results.scoreArray)-1
    # jMax = np.argmax(results.scoreArray[i, :])
    # bestAutomata = results.automataArray[i, jMax]

    automata = Automata().initBaseAutomata()
    behaviourTree = BehaviourTree().initCommunicatingAgent(44, -1)

    simSettings = SimSettings(5, 6, 0.6, 0, 0.1, 0.03, 1)
    mapSettings = FourRoomsMapSettings(18, 6, 6, 1, 20, 300, 1, 2, 4, 8)
    map = FourRoomsMap(mapSettings).init()
    pathfinder = Pathfinder(map).init()

    # mapSettings = TestMapSettings(20, 22, 6, 10)
    # map = TestMap(mapSettings).init()
    # pathfinder = Pathfinder(map).init()

    # t0 = time.time()
    # runAsync(runSimHidden, 50, [map, behaviourTree, simSettings, 1000])
    # print(time.time() - t0)

    runSim(map, behaviourTree, simSettings, pathfinder)
























