
#-----Imports-----#
import math
import numpy as np


class ChunkManager():

    def __init__(self, dx, dy, Lx, Ly):

        self.dx = dx
        self.dy = dy
        self.Lx = Lx
        self.Ly = Ly
        self.Nx = math.ceil(Lx / dx)
        self.Ny = math.ceil(Ly / dy)

        self.initChunks()

    def initChunks(self):

        self.chunks = np.full((self.Nx, self.Ny),{}, dtype=dict)
        self.neighbourChunks = np.full((self.Nx, self.Ny),{}, dtype=dict)

        for i in range(self.Nx):
            for j in range(self.Ny):
                self.chunks[i, j] = {}
                self.neighbourChunks[i, j] = {}

    def hash(self, x, y):
        return int(x / self.dx), int(y / self.dy)

    def get(self, xi, yi):
        return list(self.chunks[xi, yi].values())

    def add(self, x, y):
        xi, yi = self.hash(x, y)

        self.chunks[xi, yi][str(x)+str(y)] = [x,y]

        xmin, ymin = max(0, xi-1), max(0, yi-1)
        xmax, ymax = min(self.Nx-1,xi+1), min(self.Ny-1,y+1)

        for xii in range(xmin, xmax+1):
            for yii in range(ymin, ymax+1):
                self.neighbourChunks[xii, yii][str(x)+str(y)] = [x,y]

    def remove(self, x, y):
        xi, yi = self.hash(x, y)
        del self.chunks[xi, yi][str(x)+str(y)]

        xmin, ymin = max(0, xi-1), max(0, yi-1)
        xmax, ymax = min(self.Nx-1,xi+1), min(self.Ny-1,y+1)

        for xii in range(xmin, xmax+1):
            for yii in range(ymin, ymax+1):
                del self.neighbourChunks[xii, yii][str(x)+str(y)]

    def getNeighbours(self, x, y):
        xi, yi = self.hash(x, y)

        return list(self.neighbourChunks[xi, yi].values())


        # xiCenter, yiCenter = self.hash(x, y)
        #
        # xmin, ymin = max(0, xiCenter-1), max(0, yiCenter-1)
        # xmax, ymax = min(self.Nx-1,xiCenter+1), min(self.Ny-1,yiCenter+1)
        #
        # output = []
        # for xi in range(xmin, xmax+1):
        #     for yi in range(ymin, ymax+1):
        #         output += self.get(xi,yi)
        #
        # return output