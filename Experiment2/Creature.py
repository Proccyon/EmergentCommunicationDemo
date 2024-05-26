
#-----Imports-----#
import numpy as np


class Creature:

    def __init__(self, energy, x, y, network, gen, id):

        self.energy = energy
        self.x = x
        self.y = y
        self.network = network
        self.id = id
        self.gen = gen
        self.destination = np.array([0, 0])
        self.hasDestination = False
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

        self.shareMemory(sim)

    def eat(self, sim):

        if sim.hasFoodArray[self.x, self.y]:


            color = sim.foodColorArray[self.x, self.y]
            d = self.network.decide(color)
            dE = sim.getFoodEnergy(color)

            if dE > 0:
                sim.posEnergyEatenLog.add(d)
            else:
                sim.negEnergyEatenLog.add(d)

            if d:
                self.energy += dE
                self.network.updateMemory(color, dE)
                sim.energyEatenLog.add(dE)

            sim.hasFoodArray[self.x, self.y] = False
            sim.foodChunkManager.remove(self.x, self.y)



    def walk(self, sim):

        pos = np.array([self.x, self.y])

        freeDirections = self.getFreeDirections(sim)
        if sim.hasFoodArray[self.x, self.y] or len(freeDirections) == 0:
            return

        # If food at destination is already eaten or creature is already at destination -> remove destination
        if self.hasDestination:

            if not sim.hasFoodArray[self.destination[0], self.destination[1]]:
                self.hasDestination = False
            if (self.x == self.destination[0]) and (self.y == self.destination[1]):
                self.hasDestination = False

        # If no current destination, find new destination
        if not self.hasDestination:

            # Get all nearby food
            nearbyFoodPositions = sim.foodChunkManager.getNeighbours(self.x, self.y)

            # If no nearby food exists, walk randomly
            if len(nearbyFoodPositions) == 0:
                dp = freeDirections[np.random.randint(len(freeDirections))]
                return self.move(self.x+dp[0], self.y+dp[1], sim)

            # Find closest food
            dSquared = [np.sum((pos - np.array(posFood))**2) for posFood in nearbyFoodPositions]
            iMin = np.argmin(dSquared)

            # If closest food is outside range, walk randomly
            if dSquared[iMin] > sim.creatureSmellRange**2:
                dp = freeDirections[np.random.randint(len(freeDirections))]
                return self.move(self.x+dp[0], self.y+dp[1], sim)
            # Otherwise set closest food as destination
            else:
                self.destination = nearbyFoodPositions[iMin]
                self.hasDestination = True

        dx, dy = self.destination - pos
        absDx, absDy = np.absolute(dx), np.absolute(dy)

        # If at destination we need not move
        if absDx + absDy == 0:
            return

        # Otherwise walk in direction of destination
        xNew, yNew = self.x + np.sign(dx), self.y + np.sign(dy)

        if absDx > absDy and self.isFree(xNew, self.y, sim):
            return self.move(xNew, self.y, sim)
        if self.isFree(self.x, yNew, sim):
            return self.move(self.x, yNew, sim)



    def walkOld(self, sim):


        freeDirections = self.getFreeDirections(sim)
        if sim.hasFoodArray[self.x, self.y] or len(freeDirections) == 0:
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

    def shareMemory(self, sim):

        for direction in self.getOccupiedDirections(sim):
            otherCreature = sim.creatureArray[self.x+direction[0], self.y+direction[1]]

            if np.random.random() < sim.memoryShareChance:
                otherCreature.network.memory = np.copy(self.network.memory)


    def replicate(self, sim):

        if self.energy < sim.creatureOffspringEnergy:
            return

        directions = self.getFreeDirections(sim)

        if len(directions) == 0:
            return

        direction = directions[np.random.randint(len(directions))]

        xChild, yChild = self.x+direction[0], self.y+direction[1]
        childEnergy = self.energy / 2
        childNetwork = self.network.copy()

        sim.addCreature(xChild, yChild, childEnergy, self.gen + 1, childNetwork)

        self.energy = childEnergy

    def isFree(self, x, y, sim):
        return x >= 0 and x <= sim.Lx-1 and y >= 0 and y <= sim.Ly-1 and sim.creatureArray[x, y] == None


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