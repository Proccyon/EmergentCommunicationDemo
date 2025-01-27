
#-----Import-----#
import numpy as np


class Agent:

    def __init__(self, x: int, y: int, id: int):

        self.currentNode = 0
        self.x = x
        self.y = y
        self.id = id

        self.isHoldingFood = False
        self.foodDensity = 0

        self.boolArray = np.full(10, False, bool)
        self.counterArray = np.full(10, 0, int)
        self.floatArray = np.full(10, 0, float)
        self.coordsArray = np.full((10,2), -1, int)

        self.foodCoords = None
        self.waypointCoords = None
        self.targetAgent = None
        self.isDone = False
        self.queriedAgent = None
        self.nearbyAgentList = None

    def move(self, xNew: int, yNew: int, sim):

        if xNew < 0 or yNew < 0 or xNew >= sim.Lx or yNew >= sim.Ly:
            return

        for i, creature in enumerate(sim.creatureArray[self.x, self.y]):
            if creature.id == self.id:
                del sim.creatureArray[self.x, self.y][i]
                break

        self.x = xNew
        self.y = yNew

        sim.creatureArray[xNew, yNew].append(self)

    def gatherFood(self, sim):

        # If no food at current position or already has food we are done
        if not sim.hasFoodArray[self.x, self.y] or self.isHoldingFood:
            return

        # Remove food from the ground
        sim.removeFood(self.x, self.y, 1)
        self.isHoldingFood = True
        self.foodDensity = sim.foodDensityArray[self.x, self.y]

    def dropOffFood(self, sim):
        sim.score += self.foodDensity
        sim.foodCollected += 1
        sim.bestGatheredDensity = max(sim.bestGatheredDensity, self.foodDensity)
        self.removeFood()

    def removeFood(self):
        self.isHoldingFood = False
        self.foodDensity = 0

    def resetTarget(self, sim):

        targetAgent = self.targetAgent
        if targetAgent is None:
            return

        distance = sim.getDistance(self.x, self.y, targetAgent.x, targetAgent.y)
        if distance > sim.commRange:
            self.targetAgent = None

    def getNearbyAgents(self, sim):

        if self.nearbyAgentList is not None:
            return self.nearbyAgentList
        else:
            agentList = []
            for queriedAgent in sim.agentList:
                if self.id == queriedAgent.id:
                    continue
                distance = sim.getDistance(self.x, self.y, queriedAgent.x, queriedAgent.y)
                if distance <= sim.commRange:
                    agentList.append(queriedAgent)

            self.nearbyAgentList = agentList
            return agentList





