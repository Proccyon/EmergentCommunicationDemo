
#-----Imports-----#
import numpy as np
import pyglet
from pyglet import shapes
import colorsys

green = [6, 204, 13]
brown = [124, 99, 47]
red = [204, 6, 6]
creatureBlue = [255, 255, 255]
white = [222, 221, 215]
blue = [127, 239, 239]
black = [0, 0, 0, 255]

def drawFPS(sim, batch):

    yMax = sim.Ly * sim.creatureSize

    fps = 1 / sim.dtLog.pastAverage(3)

    text = str(np.round(fps, 2)) + "FPS"

    textDrawing = pyglet.text.Label(text, x=0, y=yMax - 15, batch=batch, color=[235, 231, 16, 255])
    return textDrawing

def calculateFoodColor(x, xMin, xMax):
    cGood = np.array(colorsys.rgb_to_hsv(*green))
    cBad = np.array(colorsys.rgb_to_hsv(*red))
    X = (x - xMin) / (xMax - xMin)
    X = max(0, X)
    X = min(1, X)
    color = cBad + (cGood - cBad) * X
    color = colorsys.hsv_to_rgb(*color)
    return [int(color[i]) for i in range(3)]


def drawFood(sim, batch):

    size = sim.creatureSize
    foodDensities = sim.foodDensityArray[sim.hasFoodArray]
    minDensity = int(np.amin(foodDensities))
    maxDensity = int(np.amax(foodDensities))
    r, g = np.array(red), np.array(green)

    foodDrawings = []
    for x in range(sim.Lx):
        for y in range(sim.Ly):

            if not sim.hasFoodArray[x, y] or sim.hasWallArray[x, y]:
                continue

            density = sim.foodDensityArray[x, y]
            color = calculateFoodColor(density, minDensity, maxDensity)
            foodDrawing = shapes.Rectangle(size * x, size * y, size, size, color=color, batch=batch)
            foodDrawings.append(foodDrawing)

    return foodDrawings

def drawCentre(sim, batch):


    size = sim.creatureSize

    xL, xR = size * sim.colonyX, size * (sim.colonyX + 1)
    yB, yT = size * sim.colonyY, size * (sim.colonyY + 1)

    line1 = shapes.Line(xL, yB, xL, yT, width=size * 0.2, color=blue, batch=batch)
    line2 = shapes.Line(xL, yT, xR, yT, width=size * 0.2, color=blue, batch=batch)
    line3 = shapes.Line(xR, yT, xR, yB, width=size * 0.2, color=blue, batch=batch)
    line4 = shapes.Line(xR, yB, xL, yB, width=size * 0.2, color=blue, batch=batch)

    return [line1, line2, line3, line4]



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
    r, g = np.array(red), np.array(green)
    foodDensities = sim.foodDensityArray[sim.hasFoodArray]
    minDensity = int(np.amin(foodDensities))
    maxDensity = int(np.amax(foodDensities))

    waypointDrawings = []
    for creature in sim.agentList:

        xWaypoint, yWaypoint = creature.coordsArray[0, :]
        if xWaypoint < 0 or yWaypoint < 0:
            continue

        xL, xR = size * xWaypoint, size * (xWaypoint + 1)
        yB, yT = size * yWaypoint, size * (yWaypoint + 1)

        color = [90, 95, 196]
        line1 = shapes.Line(xL, yB, xR, yT, width=size * 0.2, color=color, batch=batch)
        line2 = shapes.Line(xR, yB, xL, yT, width=size * 0.2, color=color, batch=batch)

        waypointDrawings.append(line1)
        waypointDrawings.append(line2)

    for creature in sim.agentList:

        if creature.isHoldingFood:
            foodColor = calculateFoodColor(creature.foodDensity, minDensity, maxDensity)
            color = [int(0.6 * creatureBlue[i] + 0.4 * foodColor[i]) for i in range(len(creatureBlue))]
        else:
            color = creatureBlue

        creatureDrawing = shapes.Circle(size * (creature.x + 0.5), size * (creature.y + 0.5), 0.5 * size, color=color, batch=batch)
        creatureDrawings.append(creatureDrawing)

    return waypointDrawings, creatureDrawings

def drawSidebar(sim, batch):

    xMax = sim.Lx * sim.creatureSize
    yMax = sim.Ly * sim.creatureSize
    L = sim.sidebarLength
    background = shapes.Rectangle(xMax, 0, L, yMax, color=white, batch=batch)

    return background

def drawFoodCollected(sim, batch):

    xOffset = 30
    yOffset = 70
    xMax = sim.Lx * sim.creatureSize + xOffset
    yMax = sim.Ly * sim.creatureSize - yOffset

    dy = 20
    dx = 100

    title1 = "Score:"
    title2 = "time:"
    text1 = str(int(sim.score))
    text2 = str(sim.t)

    drawing1 = pyglet.text.Label(title1, x=xMax, y=yMax, batch=batch, color=black, font_size=20)
    drawing2 = pyglet.text.Label(text1, x=xMax+dx, y=yMax, batch=batch, color=black, font_size=20)
    drawing3 = pyglet.text.Label(title2, x=xMax, y=yMax-dy, batch=batch, color=black, font_size=20)
    drawing4 = pyglet.text.Label(text2, x=xMax+dx, y=yMax-dy, batch=batch, color=black, font_size=20)
    return [drawing1, drawing2, drawing3, drawing4]


def drawFoodValues(sim, batch):

    yoffset = 150
    yMax = sim.Ly * sim.creatureSize - yoffset

    xOffsetRate = 0.25
    xOffset = xOffsetRate * sim.sidebarLength
    height = 50
    xMin = int(sim.Lx * sim.creatureSize + 0.5 * xOffset)
    xMax = int(sim.Lx * sim.creatureSize + sim.sidebarLength - 0.5 * xOffset)
    dy = 50
    foodDensities = sim.foodDensityArray[sim.hasFoodArray]
    minDensity = str(int(np.amin(foodDensities)))
    maxDensity = str(int(np.amax(foodDensities)))

    drawings = []


    title = pyglet.text.Label("Food Values", x=xMin, y=yMax, batch=batch, color=black, font_size=20)
    minValueDrawing = pyglet.text.Label(minDensity, x=xMin-7, y=yMax-dy+6, batch=batch, color=black, font_size=20)
    maxValueDrawing = pyglet.text.Label(maxDensity, x=xMax-7, y=yMax - dy+6, batch=batch, color=black, font_size=20)
    drawings.append(title)
    drawings.append(minValueDrawing)
    drawings.append(maxValueDrawing)

    for x in range(xMin, xMax):
        color = calculateFoodColor(x, xMin, xMax)
        sliceDrawing = shapes.Rectangle(x, yMax - height - dy, 1, height, color=color, batch=batch)
        drawings.append(sliceDrawing)

    minLine = shapes.Rectangle(xMin, yMax - height - dy, 2, height, color=black, batch=batch)
    maxLine = shapes.Rectangle(xMax, yMax - height - dy, 2, height, color=black, batch=batch)
    drawings.append(minLine)
    drawings.append(maxLine)

    return drawings

def drawHasAntMill(sim, batch):

    def getColor(bool):
        if bool:
            return red + [255]
        else:
            return green + [255]

    def getText(bool):
        if bool:
            return "Yes"
        else:
            return "No"

    yoffset = 300
    xOffset = 30
    yMax = sim.Ly * sim.creatureSize - yoffset
    xMax = sim.Lx * sim.creatureSize + xOffset
    dx = 220
    dy = 30

    hasAntMill, foodConstraint, waypointConstraint = sim.determineIfAntMill()
    titles = ["Has Ant Mill = ", "Food Constraint = ", "Waypoint Constraint = "]
    bools = [hasAntMill, foodConstraint, waypointConstraint]
    drawings = []

    for i in range(len(titles)):
        title = pyglet.text.Label(titles[i], x=xMax, y=yMax - i * dy, batch=batch, color=black, font_size=15)
        label = pyglet.text.Label(getText(bools[i]), x=xMax + dx, y=yMax - i * dy, batch=batch, color=getColor(bools[i]), font_size=15)
        drawings.append(title)
        drawings.append(label)

    return drawings


def drawStatic(sim):

    wallDrawings = drawWalls(sim, sim.batch)
    sidebar = drawSidebar(sim, sim.batch)
    foodValues = drawFoodValues(sim, sim.batch)
    centre = drawCentre(sim, sim.batch)

    return [wallDrawings, foodValues, sidebar, centre]

def draw(sim):

    sim.window.clear()

    # batch = pyglet.graphics.Batch()

    foodDrawings = drawFood(sim, sim.batch)
    waypointDrawings, creatureDrawings = drawCreatures(sim, sim.batch)

    fps = drawFPS(sim, sim.batch)
    foodCollected = drawFoodCollected(sim, sim.batch)
    hasAntMill = drawHasAntMill(sim, sim.batch)

    buttonDrawings = []
    for button in sim.buttons:
        buttonDrawings.append(button.draw(sim.batch))

    sim.batch.draw()