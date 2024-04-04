
#-----Imports-----#
import numpy as np
import pyglet
from pyglet import shapes

class Creature:

    def __init__(self, energy, x, y, id):

        self.energy = energy
        self.x = x
        self.y = y
        self.id = id

    def destroy(self, sim):
        sim.creatureArray[self.x,self.y] = None

        placement = 0
        for i, creature in enumerate(sim.creatureList):
            if self.id == creature.id:
                placement = i
                break

        print("creature destroyed")
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

        if sim.foodArray[self.x, self.y] > 0:
            return

        r = sim.creatureSmellRange
        xmin, xmax = max(0, self.x - r), min(sim.Lx-1, self.x + r + 1)
        ymin, ymax = max(0, self.y - r), min(sim.Ly-1, self.y + r + 1)

        foods = sim.foodArray[xmin:xmax, ymin:ymax]

        sUp = np.sum(foods[:, r+1:2*r+1])
        sDown = np.sum(foods[:, 0:r])
        sRight = np.sum(foods[r+1:2*r+1, :])
        sLeft = np.sum(foods[0:r, :])

        directions = [[0, 1], [0, -1], [1, 0], [-1, 0]]
        if sUp+sDown+sRight+sLeft == 0:
            dp = directions[np.random.randint(4)]
        else:
            dp = np.array(directions[np.argmax([sUp, sDown, sRight, sLeft])])

        self.move(self.x+dp[0], self.y+dp[1], sim)

    def replicate(self, sim):

        if self.energy < sim.creatureOffspringEnergy:
            return

        directions = []
        if self.x > 0 and sim.creatureArray[self.x-1, self.y] == None:
            directions.append([-1,0])
        if self.x < sim.Lx-1 and sim.creatureArray[self.x+1, self.y] == None:
            directions.append([1,0])
        if self.y > 0 and sim.creatureArray[self.x, self.y-1] == None:
            directions.append([0,-1])
        if self.y < sim.Ly-1 and sim.creatureArray[self.x, self.y+1] == None:
            directions.append([0,1])

        if len(directions) == 0:
            return

        direction = directions[np.random.randint(len(directions))]

        sim.addCreature(self.x+direction[0], self.y+direction[1], self.energy / 2)
        self.energy /= 2




class Simulation:


    def __init__(self, Lx, Ly):

        self.Lx, self.Ly = Lx, Ly

        self.creatureArray = np.empty((Lx,Ly), dtype=Creature)
        self.creatureList = []
        self.foodArray = np.zeros((Lx,Ly), dtype=float)

        self.foodSpawnChance = 0.001  # Food spawn chance per tile per tick
        self.foodInitEnergy = 100

        self.creatureSpawnChance = 0.05  # Creature spawn chance per tile per tick
        self.creatureInitEnergy = 100
        self.creatureOffspringEnergy = 200

        self.creatureEatEnergy = 5
        self.creatureDrainEnergy = 1.2

        self.creatureSmellRange = 3

        self.windowSize = 500

        self.creatureSize = 15

        self.idCounter = 0


        self.spawnCreatures()

    def addCreature(self, x, y, energy):

        creature = Creature(energy, x, y, self.idCounter)
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
            self.addCreature(x, y, self.creatureInitEnergy)

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

    def step(self):

        self.spawnFood()

        self.creatureWalk()
        self.creatureFeeding()
        self.creatureEnergyDrain()
        self.creatureReplicate()

        creaturesToDestroy = []
        for creature in self.creatureList:
            if creature.energy <= 0:
                creaturesToDestroy.append(creature)

        for creature in creaturesToDestroy:
            creature.destroy(self)

    def draw(self):

        self.window.clear()

        batch = pyglet.graphics.Batch()

        size = self.creatureSize

        foodDrawings = []
        for x in range(self.Lx):
            for y in range(self.Ly):

                s = self.foodArray[x, y] / self.foodInitEnergy
                foodColor = (int(s*50), int(s*225), int(s*30))
                foodDrawing = shapes.Rectangle(size * x, size * y, size, size, color=foodColor, batch=batch)
                foodDrawings.append(foodDrawing)

        creatureDrawings = []
        for creature in self.creatureList:
            s = min(1, creature.energy / self.foodInitEnergy)
            creatureColor = (int(55), int(s*55), int(s*255))
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




sim = Simulation(50, 50)

sim.run()