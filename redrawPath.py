# LOOKS GOOD but not so accurate
# AND cannot follow pitches correctly (?)

import pathmakerNotes as pmN
import os
import cmu_112_graphics as graphics

myfile = 'file_example_WAV_1MG.wav'
mydir = r'C:\Users\Amy\15-112\termProject\aubio_demo\sampleAudio'

fileName = mydir + os.sep + myfile
song = fileName

newPath = pmN.Path(fileName).getPath()
frames = pmN.Path(fileName).getFrames()

from cmu_112_graphics import *
from tkinter import *
import random
import numpy as np
import scipy
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.interpolate import splev, splrep

# Plan: Implement this into GameMode
# Use self.player.scrollX, etc.
# Design & add background, which will basically be drawn like the dots

class SideScrollerPath(App):
    def appStarted(self):
        # Sidescroller
        self.scrollX = 0
        self.count = 0
        # Path
        self.path = newPath
        self.frames = frames
        self.x = self.width//2
        self.y = self.height//2

    def getPath(self):
        yValue = []
        for frame in self.path:
            note = self.path[frame]
            # Keep y values in the middle third of the canvas
            yValue.append((frame, note*self.height/3 + self.height/3))
        return yValue
    
    def getFrames(self):
        return self.frames

    def getCoordinates(self):
        path = self.getPath()
        # convert list to tuple and add fill & smooth
        coordinates = []
        for i in range(len(path)):
            value = path[i][1]
            frame = path[i][0] - self.scrollX
            coordinates.extend([frame, value])
        coordinates = tuple(coordinates)
        return coordinates
    
    def getCoordinatesInTuples(self):
        path = self.getPath()
        # convert list to tuple and add fill & smooth
        coordinates = []
        for i in range(len(path)):
            value = path[i][1]
            frame = path[i][0] - self.scrollX
            coordinates.append((frame, value))
        return coordinates

    def getCoordinateFunction(self):
        coordinates = self.getCoordinatesInTuples()
        n = len(coordinates)
        # Use numpy matrix algebra
        # Create & plug in an nxn array
        xVals = []
        yVals = []
        for coord in coordinates:
            xVals.append(coord[0])
            yVals.append(coord[1])

        # x = xVals
        # y = yVals
        # sp1 = splrep(xVals, yVals, s = 100.0)
        # x2 = np.linspace(0, xVals[-1])
        # y2 = splev(x2, sp1)
        # plt.plot(x, y, 'o', x2, y2, 'b')
        # plt.show()

        return self.width//2

    def keyPressed(self, event):
        # Add:
        # HIGH attack - w
        # LOW  attack - s
        # BOTH attack - w+s
        if (event.key == 'Right'):
            self.scrollX += 10

    def timerFired(self):
        self.count += 1
#        self.scrollX += 5 # if you want to scroll right

    def redrawAll(self, canvas):
        coordinates = self.getCoordinates()
        canvas.create_line(coordinates, fill = 'red', width = 5, smooth = 1)

        # draw the player fixed to the center of the scrolled canvas
        cr = 10
        cy = self.getCoordinateFunction()
        #cy = self.getYValue(cx-self.scrollX)
        canvas.create_oval(self.x-cr, cy-cr, self.x+cr, cy+cr, fill='cyan')

        # draw the x and y axes
        x = self.width/2 - self.scrollX # <-- This is where we scroll the axis!
        y = self.height/2
        canvas.create_line(x, 0, x, self.height)
        canvas.create_line(0, y, self.width, y)

        # draw the instructions and the current scrollX
        x = self.width/2
        canvas.create_text(x, 20, text='Use arrows to move left or right')
        canvas.create_text(x, 40, text=f'app.scrollX = {self.scrollX}')

SideScrollerPath(width=1000, height=800)

# NOTE: Ends at approximately 5000 pixels