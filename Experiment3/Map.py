
#-----Imports-----#
import numpy as np
from Pathfinder import Pathfinder


class MapSettings():

    def __init__(self):
        pass

    def toString(self) -> str:
        return ""

class Map:

    def __init__(self, Lx, Ly, colonyX, colonyY, creatureCount):

        self.Lx, self.Ly = Lx, Ly
        self.colonyX, self.colonyY = colonyX, colonyY
        self.creatureCount = creatureCount
        self.foodAmountArray = np.zeros((Lx, Ly), dtype=int)
        self.foodDensityArray = np.zeros((Lx, Ly), dtype=float)
        self.hasWallArray = np.full((Lx, Ly), True, dtype=bool)
        self.creatureAmountArray = np.zeros((Lx, Ly), dtype=int)
        self.neighbourArray = np.empty((Lx, Ly),dtype=list)

        self.name = ""

    def setupNeighbours(self):

        for x in range(self.Lx):
            for y in range(self.Ly):
                neighbours = []
                for dx, dy in [(1,0),(0,1),(-1,0),(0,-1)]:
                    xNew, yNew = x+dx, y+dy
                    if self.isValidPosition(xNew, yNew):
                        neighbours.append((xNew, yNew))
                self.neighbourArray[x, y] = neighbours

    def isValidPosition(self, x, y):
        return x >= 0 and y >= 0 and x < self.Lx and y < self.Ly and not self.hasWallArray[x, y]

    def init(self):
        print("Generating map...")
        self.generate()
        self.setupNeighbours()
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


    # Calculate the maximum possible score in a given time
    def calculateMaxScore(self, tMax, popSize, pathfinder):

        # First we retrieve data about all the food in the map
        foodAmountList = []
        foodDensityList = []
        foodDistanceList = []
        for x in range(self.Lx):
            for y in range(self.Ly):
                if self.foodAmountArray[x, y] == 0:
                    continue

                foodAmountList.append(self.foodAmountArray[x, y])
                foodDensityList.append(self.foodDensityArray[x, y])
                distance = pathfinder.getDistance(self.colonyX, self.colonyY, x, y)
                if distance == 0:
                    distance = 1
                foodDistanceList.append(distance)

        foodAmountList = np.array(foodAmountList)
        foodDensityList = np.array(foodDensityList)
        foodDistanceList = np.array(foodDistanceList)

        # Calculate rate at which each food piece can generate score
        gatherRateList = foodDensityList / (2 * foodDistanceList + 1)

        # Now we sort food based on which gives most score per tick
        idList = np.argsort(-gatherRateList)

        foodAmountList = foodAmountList[idList]
        foodDensityList = foodDensityList[idList]
        gatherRateList = gatherRateList[idList]

        # Calculate how long it would take to gather each piece of food
        dtList = foodAmountList * foodDensityList / (popSize * gatherRateList)

        # Calculate total score obtained when food piece is fully gathered
        scorePerFoodList = foodAmountList * foodDensityList

        # Now calculate score obtained when food is gathered in most efficient order
        t = 0
        score = 0
        for i in range(len(idList)):
            dt = dtList[i]
            tNew = t + dt
            if tNew < tMax:
                score += scorePerFoodList[i]
                t = tNew
            else:
                score += scorePerFoodList[i] * (tMax - t) / (tNew - t)
                break

        return score

    def calculateMaxAUC(self, tMax, popSize, pathfinder):

        maxAUC = 0
        for t in range(tMax):
            maxAUC += self.calculateMaxScore(t+1, popSize, pathfinder)

        return maxAUC / tMax

    def getFileName(self) -> str:
        return ""

class TestMapSettings(MapSettings):

    def __init__(self, r, R, creatureCount, foodAmount):
        MapSettings.__init__(self)
        self.name = "TestMap"
        self.r, self.R = r, R
        self.creatureCount = creatureCount
        self.foodAmount = foodAmount

    def toString(self):

        return (f"{self.name}(\n"
                f"creature Count = {self.creatureCount}\n"
                f"r = {self.r}\n"
                f"R = {self.R}\n"
                f"foodAmount = {self.foodAmount}\n"
                f")")


class TestMap(Map):

    def __init__(self, mapSettings: TestMapSettings):

        self.r, self.R = mapSettings.r, mapSettings.R
        Lx, Ly = 2*self.R+1, 2*self.R+1
        colonyX, colonyY = self.R, self.R
        Map.__init__(self, Lx, Ly, colonyX, colonyY, mapSettings.creatureCount)

        self.foodAmount = mapSettings.foodAmount
        self.name = mapSettings.name


    def generate(self):

        self.generateWalls()
        self.generateFood()
        self.generateCreatures()

    def generateWalls(self):
        self.removeWallCirlce(self.colonyX, self.colonyY, self.r)

    def generateFood(self):

        self.placeFoodCircle(self.colonyX + 12, self.colonyY, 3, self.foodAmount, 1)
        self.placeFoodCircle(self.colonyX - 12, self.colonyY, 3, self.foodAmount, 2)
        self.placeFoodCircle(self.colonyX, self.colonyY + 12, 3, self.foodAmount, 3)

    def generateCreatures(self):
        self.creatureAmountArray[self.colonyX, self.colonyY] = self.creatureCount

    def getFileName(self) -> str:
        return f"{self.name}({self.r}, {self.R})"


class CircleMapSettings(MapSettings):

    def __init__(self, r, R, creatureCount, foodDensityRange, foodAmount):
        MapSettings.__init__(self)
        self.name = "CircleMap"
        self.r, self.R = r, R
        self.creatureCount = creatureCount
        self.foodDensityRange = foodDensityRange
        self.foodAmount = foodAmount

    def toString(self):

        return (f"{self.name}(\n"
                f"creature Count = {self.creatureCount}\n"
                f"r = {self.r}\n"
                f"R = {self.R}\n"
                f"foodDensityRange = {self.foodDensityRange}\n"
                f"foodAmount = {self.foodAmount}\n"
                f")")


class CircleMap(Map):

    def __init__(self, mapSettings: CircleMapSettings):

        self.r, self.R = mapSettings.r, mapSettings.R
        Lx, Ly = 2*self.R+1, 2*self.R+1
        colonyX, colonyY = self.R, self.R
        Map.__init__(self, Lx, Ly, colonyX, colonyY, mapSettings.creatureCount)

        self.foodDensityRange = mapSettings.foodDensityRange
        self.foodAmount = mapSettings.foodAmount
        self.name = mapSettings.name


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

            density = np.random.randint(dMin, dMax+1)
            self.foodAmountArray[x, y] += self.foodAmount
            self.foodDensityArray[x, y] = density

    def generateCreatures(self):
        self.creatureAmountArray[self.colonyX, self.colonyY] = self.creatureCount

    def getFileName(self) -> str:
        return f"{self.name}({self.r}, {self.R})"


class FourRoomsMapSettings(MapSettings):

    def __init__(self, r1, r2, d, w, creatureCount, foodAmount, f1, f2, f3, f4):
        MapSettings.__init__(self)
        self.name = "FourRooms"
        self.creatureCount = creatureCount
        self.r1, self.r2, self.d, self.w = r1, r2, d, w
        self.f1, self.f2, self.f3, self.f4 = f1, f2, f3, f4
        self.foodAmount = foodAmount

    def toString(self):

        return (f"{self.name}(\n"
                f"creature Count = {self.creatureCount}\n"
                f"r1 = {self.r1}\n"
                f"r2 = {self.r2}\n"
                f"d = {self.d}\n"
                f"w = {self.w}\n"
                f"foodAmount = {self.foodAmount}\n"
                f"f1 = {self.f1}\n"
                f"f2 = {self.f2}\n"
                f"f3 = {self.f3}\n"
                f"f4 = {self.f4}\n"
                f")")

class FourRoomsMap(Map):

    def __init__(self, mapSettings: FourRoomsMapSettings):

        self.r1, self.r2, self.d, self.w = mapSettings.r1, mapSettings.r2, mapSettings.d, mapSettings.w
        self.f1, self.f2, self.f3, self.f4 = mapSettings.f1, mapSettings.f2, mapSettings.f3, mapSettings.f4

        L = 2 * (self.r1 + self.d + 2 * self.r2) + 1
        colonyX, colonyY = int((L - 1) / 2), int((L - 1) / 2)
        Map.__init__(self, L, L, colonyX, colonyY, mapSettings.creatureCount)

        self.foodAmount = mapSettings.foodAmount
        self.name = mapSettings.name

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

    def getFileName(self) -> str:
        return f"{self.name}({self.r1}, {self.r2}, {self.d}, {self.w})"

def getMapDict():

    mapList = [("CircleMap", CircleMap), ("FourRooms", FourRoomsMap)]
    mapDict = {}

    for name, map in mapList:
        mapDict[name] = map

    return mapDict






