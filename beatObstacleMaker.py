import beatsParser as bP
import cmu_112_graphics as cmug
import os

mydir = r'C:\Users\Amy\15-112\termProject\aubio_demo\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile
song = fileName

class BeatObstacles(cmug.App):
    def __init__(self, song):
        super().__init__()
        self.song = song

    def appStarted(self):
        self.beatObj = bP.Beats(song)
        self.beats = self.beatObj.getBeats()
        self.beatVals = set(self.beats)
        self.values = set()
        for val in self.beatVals:
            self.values.add(round(val))
        self.count = 0
        self.frames = self.beatObj.totalFrames
        self.color = 'red'

    def timerFired(self):
        if (round(self.count) in self.values):
            self.color = 'blue'
        else:
            self.color = 'red'
        self.count += 0.1

    def redrawAll(self, canvas):
        r = 20
        x = self.width//2
        y = self.height//2
        canvas.create_oval(x-r,y-r,x+r,y+r,fill=self.color)

test = BeatObstacles(song)