# Pros: FUNCTIONS, dot can FOLLOW path
# Cons: seems incredibly slow and inaccurate, or at least not as interestingly curved
#


import pathmakerPitch as pmp
import cmu_112_graphics as cmug
import os
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np

class PitchPathmaker(cmug.App):
    def __init__(self, song):
        super().__init__()
        self.song = song
    
    def appStarted(self):
        self.timerDelay = 1

        self.pitchPath = pmp.PitchPath(song)
        self.path = self.pitchPath.getPitchPath() # Dictionary of frames to pitch
        self.frames = self.pitchPath.totalFrames # Total frames in pitchPath
        self.range = self.pitchPath.getPitchRange() # Range of pitches
        self.minPitch = self.pitchPath.getMinPitch() # Lowest pitch

        self.r = 30 # Radius of placeholder player
        self.x = 100 # Player x value
        self.y = 0 # Player y value
        self.scrollX = 0 # Scroll x value

        self.newPath = [] # Path of (x,y) based on (frame, pitch)
        for frame in self.path:
            pitch = self.path[frame]
            yVal = self.height//4 + ((pitch-self.minPitch)/self.range)*(self.height//2)
            xVal = frame
            self.newPath.append((xVal, yVal))
    
        self.xVals = []
        path = self.newPath
        for pair in path:
            self.xVals.append(pair[0])

        self.yVals = []
        path = self.newPath
        for pair in path:
            self.yVals.append(pair[1])

        x = self.xVals
        y = self.yVals
        xnew = np.linspace(0, x, num = len(x), endpoint = True)
        self.f = interp1d(x, y, kind='cubic')
#        plt.plot(x, y, 'o', xnew, self.f(xnew), '-')
#        plt.show()

    def getCoordinates(self):
        coordinates = []
        for pair in self.newPath:
            coordinates.extend([pair[0]-self.scrollX, pair[1]])
        coords = tuple(coordinates)
        return coords

    def getPathCoords(self):
        coordinates = []
        for x in self.xVals:
            y = self.f(x)
            coordinates.extend([x, y])
        return tuple(coordinates)

    def keyPressed(self, event):
        pass
#        if (event.key == 'Right'):
#            self.scrollX += 10
#        self.y = self.f(self.x+self.scrollX)

    def timerFired(self):
        self.scrollX += 10
        self.y = self.f(self.x + self.scrollX)

    def redrawAll(self, canvas):
        # draw the x and y axes
        x = self.width/2 - self.scrollX
        y = self.height/2
        canvas.create_line(x, 0, x, self.height)
        canvas.create_line(0, y, self.width, y)

        # draw path
        path = self.newPath
        coords = self.getCoordinates()
        canvas.create_line(coords, fill='red', smooth=1)

        # draw 'player'
        canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r,self.y+self.r,fill='blue')

mydir = r'C:\Users\Amy\15-112\termProject\aubio_demo\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile
song = fileName

test = PitchPathmaker(song)