
#-----Imports-----#
import numpy as np
import pyglet
from pyglet import shapes

green = [6, 204, 13]
brown = [124, 99, 47]
red = [204, 6, 6]
creatureBlue = [255, 255, 255]
white = [222, 221, 215]

def drawFPS(sim, batch):

    yMax = sim.Ly * sim.creatureSize

    fps = 1 / sim.dtLog.pastAverage(3)

    text = str(np.round(fps, 2)) + "FPS"

    textDrawing = pyglet.text.Label(text, x=0, y=yMax - 15, batch=batch, color=[235, 231, 16, 255])
    return textDrawing


def drawFoodCollected(sim, batch):

    yMax = sim.Ly * sim.creatureSize

    text = f"Food Collected: {sim.score}\nt: {sim.t}"

    textDrawing = pyglet.text.Label(text, x=0, y=yMax - 70, batch=batch, color=white+[255], font_size=20)
    return textDrawing


def drawFood(sim, batch):

    size = sim.creatureSize
    minDensity = np.amin(sim.foodDensityArray)
    maxDensity = np.amax(sim.foodDensityArray)
    r, g = np.array(red), np.array(green)

    foodDrawings = []
    for x in range(sim.Lx):
        for y in range(sim.Ly):

            if not sim.hasFoodArray[x, y] or sim.hasWallArray[x, y]:
                continue

            density = sim.foodDensityArray[x, y]
            color = r + (g - r) * (density - minDensity) / (maxDensity - minDensity)
            color = [int(c) for c in color]
            foodDrawing = shapes.Rectangle(size * x, size * y, size, size, color=color, batch=batch)
            foodDrawings.append(foodDrawing)

    return foodDrawings

def drawWalls(sim, batch):

    size = sim.creatureSize

    wallDrawings = []
    for x in range(sim.Lx):
        for y in range(sim.Ly):

            if not sim.hasWallArray[x, y]:
                continue

            wallDrawing = shapes.Rectangle(size * x, size * y, size, size, color=brown, batch=batch)
            wallDrawings.append(wallDrawing)

    return wallDrawings


def drawCreatures(sim, batch):

    creatureDrawings = []
    size = sim.creatureSize

    for creature in sim.agentList:

        if creature.isHoldingFood:
            color = [int(0.75 * creatureBlue[i] + 0.25 * green[i]) for i in range(len(creatureBlue))]
        else:
            color = creatureBlue

        creatureDrawing = shapes.Circle(size * (creature. x +0.5), size * (creature. y + 0.5), 0.5 * size, color=color, batch=batch)
        creatureDrawings.append(creatureDrawing)

    return creatureDrawings

def drawSidebar(sim, batch):

    xMax = sim.Lx * sim.creatureSize
    yMax = sim.Ly * sim.creatureSize
    L = sim.sidebarLength
    background = shapes.Rectangle(xMax, 0, L, yMax, color=white, batch=batch)
    return background


def draw(sim):

    sim.window.clear()

    # batch = pyglet.graphics.Batch()

    foodDrawings = drawFood(sim, sim.batch)
    creatureDrawings = drawCreatures(sim, sim.batch)

    sidebar = drawSidebar(sim, sim.batch)
    fps = drawFPS(sim, sim.batch)
    foodCollected = drawFoodCollected(sim, sim.batch)

    buttonDrawings = []
    for button in sim.buttons:
        buttonDrawings.append(button.draw(sim.batch))

    sim.batch.draw()