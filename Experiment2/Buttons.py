
#-----Imports-----#
import pyglet
from pyglet import shapes

class Slider:

    def __init__(self, x, y, width, height, color, text):

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.on = False
        self.text = text


    def draw(self, batch):

        R = 0.5 * self.height
        Bh = self.height
        Bw = self.width - self.height

        xC1 = self.x+R
        xC2 = self.x+R+Bw
        yC = self.y+R

        #Draw background
        c1 = shapes.Circle(xC1, yC, R, color=self.color,
                      batch=batch)
        b = shapes.Rectangle(self.x+R, self.y, Bw, Bh, color=self.color, batch=batch)
        c2 = shapes.Circle(xC2, yC, R, color=self.color,
                      batch=batch)

        xText = self.x + 0.5 * self.width
        yText = self.y + self.height + 0.5 * self.height

        textDrawing = pyglet.text.Label(self.text, x=xText, y=yText, batch=batch, anchor_x='center', anchor_y='center', color=[0, 0, 0, 255])

        if self.on:
            xDot = xC2
        else:
            xDot = xC1

        cDot = shapes.Circle(xDot, yC, 0.8 * R, color=[0,0,0,255],
                      batch=batch)

        return [c1, b, c2, cDot, textDrawing]

    def isClicked(self, x, y):
        return (self.x < x < self.x + self.width and
                self.y < y < self.y + self.height)

    def onClick(self, sim):
        self.on = not self.on