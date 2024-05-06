
#-----Imports-----#
import numpy as np
import pyglet
from pyglet import shapes
import time
import matplotlib.pyplot as plt

from CommNetwork import CommNetwork

class Creature:

    def __init__(self, energy, x, y, id, network, canMutate):

        self.energy = energy
        self.x = x
        self.y = y
        self.id = id
        self.network = network
        self.toBeDestroyed = False
        self.battledCreatures = []
        self.canMutate = canMutate

    def destroy(self, sim):

        if self.toBeDestroyed:
            sim.bloodArray[self.x, self.y] += 100

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

    def eat(self, sim, eatEnergy):

        foodEnergy = sim.foodArray[self.x, self.y]
        energyDiff = eatEnergy

        if foodEnergy < eatEnergy:
            energyDiff = foodEnergy

        self.energy += energyDiff
        sim.foodArray[self.x, self.y] -= energyDiff


    def walk(self, sim):

        freeDirections = self.getFreeDirections(sim)
        if sim.foodArray[self.x, self.y] > 0 or len(freeDirections) == 0:
            return

        r = sim.creatureSmellRange
        xmin, xmax = max(0, self.x - r), min(sim.Lx-1, self.x + r + 1)
        ymin, ymax = max(0, self.y - r), min(sim.Ly-1, self.y + r + 1)

        foods = sim.foodArray

        sUp = np.sum(foods[xmin:xmax, self.y+1:ymax])
        sDown = np.sum(foods[xmin:xmax, ymin:self.y])
        sRight = np.sum(foods[self.x+1:xmax, ymin:ymax])
        sLeft = np.sum(foods[xmin:self.x, ymin:ymax])

        # sUp = np.sum(foods[xmin:xmax, self.y+1:ymax] * (sim.creatureArray[xmin:xmax, self.y+1:ymax] == None))
        # sDown = np.sum(foods[xmin:xmax, ymin:self.y] * (sim.creatureArray[xmin:xmax, ymin:self.y] == None))
        # sRight = np.sum(foods[self.x+1:xmax, ymin:ymax] * (sim.creatureArray[self.x+1:xmax, ymin:ymax] == None))
        # sLeft = np.sum(foods[xmin:self.x, ymin:ymax] * (sim.creatureArray[xmin:self.x, ymin:ymax] == None))
        foodValues = np.array([sUp, sDown, sRight, sLeft])

        directions = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        if np.sum(foodValues) == 0:
            dp = freeDirections[np.random.randint(len(freeDirections))]
        else:
            maxDirections = directions[foodValues == np.amax(foodValues)]
            dp = np.array(maxDirections[np.random.randint(len(maxDirections))])

        self.move(self.x+dp[0], self.y+dp[1], sim)
        self.battleArea(sim)


    def replicate(self, sim):

        if self.energy < sim.creatureOffspringEnergy:
            return

        directions = self.getFreeDirections(sim)

        if len(directions) == 0:
            return

        direction = directions[np.random.randint(len(directions))]

        xChild, yChild = self.x+direction[0], self.y+direction[1]
        childEnergy = self.energy / 2
        childNetwork = self.network.copy(self.canMutate)
        sim.addCreature(xChild, yChild, childEnergy, childNetwork, self.canMutate)
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

    def battleArea(self, sim):

        for direction in self.getOccupiedDirections(sim):
            otherCreature = sim.creatureArray[self.x+direction[0], self.y+direction[1]]
            if otherCreature.id not in self.battledCreatures:
                self.battle(otherCreature)

    def battle(self, otherCreature):

        if self.toBeDestroyed or otherCreature.toBeDestroyed:
            return

        messageIn = None
        messageOut = None
        for i in range(3):
            messageOut = self.network.respond(messageIn)
            messageIn = otherCreature.network.respond(messageOut)

        otherCreature.toBeDestroyed = self.network.getDecision(messageIn)
        self.toBeDestroyed = otherCreature.network.getDecision(messageOut)

        self.battledCreatures.append(otherCreature.id)
        otherCreature.battledCreatures.append(self.id)




class Simulation:


    def __init__(self, Lx, Ly):

        self.Lx, self.Ly = Lx, Ly

        self.creatureArray = np.empty((Lx,Ly), dtype=Creature)
        self.creatureList = []
        self.foodArray = np.zeros((Lx,Ly), dtype=float)
        self.bloodArray = np.zeros((Lx, Ly), dtype=float)

        self.muteCreatureCountLog = []
        self.commCreatureCountLog = []

        self.foodSpawnChance = 0.001  # Food spawn chance per tile per tick
        self.foodInitEnergy = 50

        self.creatureSpawnChance = 0.05  # Creature spawn chance per tile per tick
        self.creatureInitEnergy = 100
        self.creatureOffspringEnergy = 200

        self.creatureEatEnergy = 5
        self.creatureDrainEnergy = 1

        self.bloodDecayRate = 1

        self.creatureSmellRange = 3

        self.windowSize = 500

        self.creatureSize = 8

        self.idCounter = 0

        self.messageSize = 3


        self.spawnCreatures()

    def addCreature(self, x, y, energy, network, canMutate):

        creature = Creature(energy, x, y, self.idCounter, network, canMutate)
        self.creatureArray[x, y] = creature
        self.creatureList.append(creature)
        self.idCounter += 1

    def spawnFood(self):

        emptySpots = np.array(np.where(self.foodArray == 0))
        emptySpotCount = len(emptySpots[0, :])

        foodSpawnCount = np.random.binomial(emptySpotCount, self.foodSpawnChance)

        filledIndices = np.random.choice(range(emptySpotCount), foodSpawnCount, False)

        for i in filledIndices:
            x, y = emptySpots[0, i], emptySpots[1, i]
            self.foodArray[x, y] = self.foodInitEnergy


    def spawnCreatures(self):

        emptySpots = np.array(np.where(self.creatureArray == None))
        emptySpotCount = len(emptySpots[0,:])

        creatureSpawnCount = np.random.binomial(emptySpotCount, self.creatureSpawnChance)

        filledIndices = np.random.choice(range(emptySpotCount), creatureSpawnCount, False)

        for i in filledIndices:
            x, y = emptySpots[0, i], emptySpots[1, i]
            canMutate = np.random.random() > 0.5

            self.addCreature(x, y, self.creatureInitEnergy, CommNetwork(self.messageSize), canMutate)

    def creatureFeeding(self):

        for creature in self.creatureList:
            creature.eat(self, self.creatureEatEnergy)

    def creatureEnergyDrain(self):

        for creature in self.creatureList:
            creature.energy -= self.creatureDrainEnergy

    def creatureWalk(self):

        for creature in self.creatureList:
            creature.walk(self)

    def creatureReplicate(self):

        for creature in self.creatureList:
            creature.replicate(self)

    def decayBlood(self):

        self.bloodArray -= self.bloodDecayRate
        self.bloodArray[self.bloodArray < 0] = 0


    def step(self):

        self.spawnFood()

        self.creatureWalk()
        self.creatureFeeding()
        self.creatureEnergyDrain()
        self.creatureReplicate()
        self.decayBlood()

        creaturesToDestroy = []
        muteCreatureCount = 0
        commCreatureCount = 0

        for creature in self.creatureList:
            if creature.energy <= 0 or creature.toBeDestroyed:
                creaturesToDestroy.append(creature)

            if creature.canMutate:
                commCreatureCount += 1
            else:
                muteCreatureCount += 1

        self.muteCreatureCountLog.append(muteCreatureCount)
        self.commCreatureCountLog.append(commCreatureCount)

        for creature in creaturesToDestroy:
            creature.destroy(self)

    def draw(self):

        self.window.clear()

        batch = pyglet.graphics.Batch()

        size = self.creatureSize

        cFood = (50, 225, 30)
        cBlood = (255, 0, 0)

        foodDrawings = []
        for x in range(self.Lx):
            for y in range(self.Ly):

                sFood = self.foodArray[x, y] / self.foodInitEnergy
                sBlood = np.amin([self.bloodArray[x, y] / 100, 1])


                if sFood + sBlood > 0:
                    color = [int(sFood * cFood[i] + sBlood * cBlood[i] - 0.5 * sFood * sBlood * (cFood[i] + cBlood[i])) for i in range(len(cFood))]
                else:
                    continue

                foodDrawing = shapes.Rectangle(size * x, size * y, size, size, color=color, batch=batch)
                foodDrawings.append(foodDrawing)

        creatureDrawings = []
        commCreatureColor = [55,55,255]
        muteCreatureColor = [200, 200, 0]
        for creature in self.creatureList:
            s = min(1, creature.energy / self.foodInitEnergy)

            if creature.canMutate:
                color = commCreatureColor
            else:
                color = muteCreatureColor
            creatureColor = [int(s * color[i]) for i in range(len(color))]
            creatureDrawing = shapes.Circle(size * (creature.x+0.5), size * (creature.y+0.5), 0.5*size, color=creatureColor, batch=batch)

            creatureDrawings.append(creatureDrawing)

        batch.draw()

    def run(self, drawGame=True):

        if (drawGame):

            self.window = pyglet.window.Window(self.Lx * self.creatureSize, self.Ly * self.creatureSize)

            @self.window.event
            def on_draw():

                self.step()
                self.draw()

            pyglet.app.run()

        if (drawGame):
            self.window.close()




sim = Simulation(100, 100)

sim.run()

plt.figure()

t = range(len(sim.commCreatureCountLog))

plt.plot(t, sim.commCreatureCountLog, color = "blue", label="comm count")
plt.plot(t, sim.muteCreatureCountLog, color = "orange", label="mute count")

plt.xlabel("Timesteps")
plt.ylabel("Creature count")

plt.xlim(0, len(t)-1)
plt.ylim(0, 1.2 * max(np.amax(sim.commCreatureCountLog), np.amax(sim.muteCreatureCountLog)))

plt.grid(linestyle="--", alpha = 0.5)

plt.legend()

plt.show()
