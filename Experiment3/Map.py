
#-----Imports-----#
import numpy as np
from Pathfinder import Pathfinder


class Map:

    def __init__(self, Lx, Ly, colonyX, colonyY, creatureCount):

        self.Lx, self.Ly = Lx, Ly
        self.colonyX, self.colonyY = colonyX, colonyY
        self.creatureCount = creatureCount
        self.foodAmountArray = np.zeros((Lx, Ly), dtype=int)
        self.foodDensityArray = np.zeros((Lx, Ly), dtype=float)
        self.hasWallArray = np.full((Lx, Ly), True, dtype=bool)
        self.creatureAmountArray = np.zeros((Lx, Ly), dtype=int)

        self.pathfinderArray = np.full((Lx, Ly), None, dtype=Pathfinder)

    def setupPathfinderArray(self):

        size = self.Lx * self.Ly
        i=0
        for x in range(self.Lx):
            for y in range(self.Ly):
                i+=1
                if self.hasWallArray[x, y]:
                    continue

                pathfinder = Pathfinder(self, x, y)
                pathfinder.init()
                self.pathfinderArray[x, y] = pathfinder

                if i % 100 == 0:
                    print(f"{i}/{size}")

    def init(self):
        print("Generating map...")
        self.generate()
        print("Setting up pathfinders...")
        self.setupPathfinderArray()
        return self

    def generate(self):
        pass

    def removeWallCirlce(self, x0, y0, r):
        for x in range(int(x0 - r)-1, int(x0 + r) + 2):
            for y in range(int(y0 - r)-1, int(y0 + r) + 2):
                if (x - x0)**2 + (y - y0)**2 <= r**2:
                    self.hasWallArray[x, y] = False

    def removeWallRectangle(self, xMin, xMax, yMin, yMax):
        self.hasWallArray[xMin:xMax+1, yMin:yMax+1] = False

    def placeFoodCircle(self, x0, y0, r, foodAmount, foodDensity):
        for x in range(int(x0 - r)-1, int(x0 + r) + 2):
            for y in range(int(y0 - r)-1, int(y0 + r) + 2):
                if (x - x0)**2 + (y - y0)**2 <= r**2:
                    self.foodAmountArray[x, y] = foodAmount
                    self.foodDensityArray[x, y] = foodDensity

class CircleMap(Map):

    def __init__(self, r, R, creatureCount, foodDensityRange, foodAmount):

        Lx, Ly = 2*R+1, 2*R+1
        colonyX, colonyY = R, R
        Map.__init__(self, Lx, Ly, colonyX, colonyY, creatureCount)
        self.r, self.R = r, R
        self.foodDensityRange = foodDensityRange
        self.foodAmount = foodAmount

    def generate(self):

        self.generateWalls()
        self.generateFood()
        self.generateCreatures()

    def generateWalls(self):
        self.removeWallCirlce(self.colonyX, self.colonyY, self.r)


    def generateFood(self):

        dMin, dMax = self.foodDensityRange
        for _ in range(self.foodAmount):
            x, y = np.random.randint(self.Lx), np.random.randint(self.Lx)
            if self.hasWallArray[x, y]:
                continue

            density = np.random.randint(dMin, dMax)
            self.foodAmountArray[x, y] += self.foodAmount
            self.foodDensityArray[x, y] = density

    def generateCreatures(self):
        self.creatureAmountArray[self.colonyX, self.colonyY] = self.creatureCount

class FourRoomsMap(Map):

    def __init__(self, r1, r2, d, w, creatureCount, foodAmount, f1, f2, f3, f4):

        L = 2 * (r1 + d + 2 * r2) + 1
        colonyX, colonyY = int((L - 1) / 2), int((L - 1) / 2)
        Map.__init__(self, L, L, colonyX, colonyY, creatureCount)
        self.r1, self.r2, self.d, self.w = r1, r2, d, w
        self.f1, self.f2, self.f3, self.f4 = f1, f2, f3, f4
        self.foodAmount = foodAmount

    def generate(self):

        self.generateWalls()
        self.generateFood()
        self.generateCreatures()

    def generateWalls(self):

        self.removeWallCirlce(self.colonyX, self.colonyY, self.r1)

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        for dx, dy in directions:
            R = self.r1 + self.r2 + self.d
            x0, y0 = self.colonyX + dx * R, self.colonyY + dy * R
            self.removeWallCirlce(x0, y0, self.r2)

            x1, y1 = self.colonyX + dy * self.w, self.colonyY + dx * self.w
            x2, y2 = self.colonyX - dy * self.w, self.colonyY - dx * self.w
            xMin, xMax = np.amin([x0, x1, x2]), np.amax([x0, x1, x2])
            yMin, yMax = np.amin([y0, y1, y2]), np.amax([y0, y1, y2])
            self.removeWallRectangle(xMin, xMax, yMin, yMax)

    def generateFood(self):

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        foodDensities = [self.f1, self.f2, self.f3, self.f4]

        for i, dir in enumerate(directions):
            dx, dy = dir
            R = self.r1 + self.r2 + self.d
            x0, y0 = self.colonyX + dx * R, self.colonyY + dy * R
            self.placeFoodCircle(x0, y0, self.r2, self.foodAmount, foodDensities[i])

    def generateCreatures(self):
        self.creatureAmountArray[self.colonyX, self.colonyY] = self.creatureCount
