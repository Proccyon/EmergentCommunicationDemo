
#-----Imports-----#
import numpy as np

class Pathfinder:

    def __init__(self, map, x0, y0):
        self.map = map
        self.Lx, self.Ly = map.Lx, map.Ly
        self.x0, self.y0 = x0, y0

        self.distanceArray = np.full((map.Lx, map.Ly), 999, dtype=np.uint16)
        self.directionArray = np.empty((map.Lx, map.Ly), dtype=list)
        self.directionDict = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}
        self.setupDirectionArray()

        #self.updateFrom(x0, y0)


    def setupDirectionArray(self):

        for x in range(self.Lx):
            for y in range(self.Ly):
                self.directionArray[x,y] = []

    def getNext(self, x, y):

        if not self.isValidPosition(x, y):
            return []

        next = []
        for ind in self.directionArray[x, y]:
            dx, dy = self.directionDict[ind]
            next.append((x + dx, y + dy))

        return next

    def getPrev(self, x, y):

        if not self.isValidPosition(x, y):
            return []

        prev = []
        for ind in self.directionDict.keys():
            if not ind in self.directionArray[x, y]:
                dx, dy = self.directionDict[ind]
                xNew, yNew = x + dx, y + dy
                if self.isValidPosition(xNew, yNew):
                    prev.append((x + dx, y + dy))

        return prev

    def getDistance(self, x, y):
        return self.distanceArray[x, y]

    def isValidPosition(self, x, y):
        return x >= 0 and y >= 0 and x < self.Lx and y < self.Ly and not self.map.hasWallArray[x, y]

    # Updates the distance and direction of a single position and returns nearby positions needing updates
    def updateTile(self, x, y, distance):

        toUpdate = set()  # Set of neighbouring positions that need updates
        directions = []  # List of directions that lead to the destination

        for ind, direction in self.directionDict.items():
            dx, dy = self.directionDict[ind]
            xNew, yNew = x+dx, y+dy
            if not self.isValidPosition(xNew, yNew):
                continue

            if self.distanceArray[xNew, yNew] > distance:
                toUpdate.add((xNew, yNew))

            if self.distanceArray[xNew, yNew] == distance - 1:
                directions.append(ind)

        self.distanceArray[x, y] = distance
        self.directionArray[x, y] = directions
        return toUpdate

    #Calculates the distance at a position based on minimum neighbour distance
    def calculateDistance(self, x, y):

        if x == self.x0 and y == self.y0:
            return 0
        else:

            distance = 999
            for ind, direction in self.directionDict.items():
                dx, dy = self.directionDict[ind]
                xNew, yNew = x + dx, y + dy
                if not self.isValidPosition(xNew, yNew):
                    continue

                distance = np.amin([distance, self.distanceArray[xNew, yNew]])

            return distance

    # Update tile distances and directions starting at position (x, y)
    def updateFrom(self, x, y, endPosition=None):

        if not self.isValidPosition(x, y):
            return

        distance = self.calculateDistance(x, y)

        currentUpdating = {(x, y)}
        nextUpdating = set()

        if endPosition is not None:
            xEnd, yEnd = endPosition
        else:
            xEnd, yEnd = -1,-1

        done = False
        while len(currentUpdating) > 0 and not done:
            for xNew, yNew in currentUpdating:
                toUpdate = self.updateTile(xNew, yNew, distance)
                nextUpdating = nextUpdating.union(toUpdate)

                if endPosition is not None and xNew == xEnd and yNew == yEnd:
                    done = True

            currentUpdating = nextUpdating
            nextUpdating = set()
            distance += 1


    def init(self, endPositions=None):
        self.updateFrom(self.x0, self.y0, endPositions)


def selectRandomPosition(sim, x, y, positions):

    d0 = np.sqrt((x-sim.colonyX)**2 + (y-sim.colonyY)**2)
    weights = [np.abs(np.sqrt((x-sim.colonyX)**2 + (y-sim.colonyY)**2) - d0) for x, y in positions]
    weights /= np.sum(weights)

    ind = np.random.choice(range(len(positions)), p=weights)
    return positions[ind]






