
#-----Imports-----#
import numpy as np
import os

class Pathfinder:

    def __init__(self, map):

        self.directionDict = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}
        self.map = map
        self.Lx, self.Ly = map.Lx, map.Ly

        self.setupTranslationArrays()

    def init(self):

        folderName = self.map.getFileName()
        if os.path.isdir(folderName):
            self.load()
        else:
            self.generateArrays()
            self.save()

        return self

    def generateArrays(self):

        n = len(self.indexToCoords)
        self.distanceArray = np.full((n, n), 999, dtype=np.uint16)
        self.directionArray = np.zeros((n, n, 4), dtype=bool)

        for i in range(n):
            x0, y0 = self.indexToCoords[i]
            self.updateFrom(x0, y0)

        return self

    def load(self):
        folderName = self.map.getFileName()
        self.distanceArray = np.load(f"{folderName}/distanceArray.npy", mmap_mode='r')
        self.directionArray = np.load(f"{folderName}/directionArray.npy", mmap_mode='r')
        return self

    def save(self):
        folderName = self.map.getFileName()
        if not os.path.isdir(folderName):
            os.makedirs(folderName)

        np.save(f"{folderName}/distanceArray.npy", self.distanceArray)
        np.save(f"{folderName}/directionArray.npy", self.directionArray)


    def setupTranslationArrays(self):

        coordsToIndex = np.full((self.Lx, self.Ly), -1, dtype=int)
        indexToCoords = []

        i = 0
        for x in range(self.Lx):
            for y in range(self.Ly):
                if self.map.hasWallArray[x, y]:
                    continue

                indexToCoords.append([x, y])
                coordsToIndex[x, y] = i
                i += 1

        self.coordsToIndex = coordsToIndex
        self.indexToCoords = np.array(indexToCoords)



    def getNext(self, x0, y0, x, y):

        if not self.map.isValidPosition(x, y):
            return []

        next = []
        for i, isTrue in enumerate(self.getDirections(x0, y0, x, y)):
            if isTrue:
                dx, dy = self.directionDict[i]
                next.append((x + dx, y + dy))

        return next

    def getPrev(self, x0, y0, x, y):

        if not self.map.isValidPosition(x, y):
            return []

        prev = []
        for i, isTrue in enumerate(self.getDirections(x0, y0, x, y)):
            if not isTrue:
                dx, dy = self.directionDict[i]
                xNew, yNew = x + dx, y + dy
                if self.map.isValidPosition(xNew, yNew):
                    prev.append((xNew, yNew))

        return prev

    def getDistance(self, x0, y0, x, y):
        i0 = self.coordsToIndex[x0, y0]
        i1 = self.coordsToIndex[x, y]

        return self.distanceArray[i0, i1]

    def setDistance(self, x0, y0, x, y, distance):
        i0 = self.coordsToIndex[x0, y0]
        i1 = self.coordsToIndex[x, y]
        self.distanceArray[i0, i1] = distance

    def getDirections(self, x0, y0, x, y):
        i0 = self.coordsToIndex[x0, y0]
        i1 = self.coordsToIndex[x, y]
        return self.directionArray[i0, i1]

    def setDirections(self, x0, y0, x, y, directions):
        i0 = self.coordsToIndex[x0, y0]
        i1 = self.coordsToIndex[x, y]
        self.directionArray[i0, i1] = directions


    # Updates the distance and direction of a single position and returns nearby positions needing updates
    def updateTile(self, x0, y0, x, y, distance):

        toUpdate = set()  # Set of neighbouring positions that need updates
        directions = np.zeros(4, dtype=bool)  # List of directions that lead to the destination

        for ind, direction in self.directionDict.items():
            dx, dy = self.directionDict[ind]
            xNew, yNew = x+dx, y+dy
            if not self.map.isValidPosition(xNew, yNew):
                continue

            newDistance = self.getDistance(x0, y0, xNew, yNew)
            if newDistance > distance:
                toUpdate.add((xNew, yNew))

            if newDistance == distance - 1:
                directions[ind] = True

        self.setDistance(x0, y0, x, y, distance)
        self.setDirections(x0, y0, x, y, directions)
        return toUpdate

    #Calculates the distance at a position based on minimum neighbour distance
    def calculateDistance(self, x, y, x0, y0):

        if x == x0 and y == y0:
            return 0
        else:

            distance = 999
            for ind, direction in self.directionDict.items():
                dx, dy = self.directionDict[ind]
                xNew, yNew = x + dx, y + dy
                if not self.map.isValidPosition(xNew, yNew):
                    continue

                distance = np.amin([distance, self.distanceArray[xNew, yNew]])

            return distance

    # Update tile distances and directions starting at position (x, y)
    def updateFrom(self, x0, y0):

        if not self.map.isValidPosition(x0, y0):
            return

        distance = self.calculateDistance(x0, y0, x0, y0)

        currentUpdating = {(x0, y0)}
        nextUpdating = set()

        while len(currentUpdating) > 0:
            for xNew, yNew in currentUpdating:
                toUpdate = self.updateTile(x0, y0, xNew, yNew, distance)
                nextUpdating = nextUpdating.union(toUpdate)

            currentUpdating = nextUpdating
            nextUpdating = set()
            distance += 1



def selectRandomPosition(sim, x, y, positions):

    d0 = np.sqrt((x-sim.colonyX)**2 + (y-sim.colonyY)**2)
    weights = [np.abs(np.sqrt((x-sim.colonyX)**2 + (y-sim.colonyY)**2) - d0) for x, y in positions]
    weights /= np.sum(weights)

    ind = np.random.choice(range(len(positions)), p=weights)
    return positions[ind]






