import lengthOfSong as lenSong
import pathmakerPitch as pmp
import beatsParser as bP
import playerClass as player
import cmu_112_graphics as cmug
import os
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# References:
# Scipy Interpolation Documentation: https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html#d-interpolation-interp1d
# CMU Graphics:
    # Animation Framework:
        # http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
    # cmu_112_graphics source:
        # http://www.cs.cmu.edu/~112/notes/hw7.html
# Matplot used only for accuracy/visualization of the interpolation function - will not be used in final version

class PitchPathmaker(cmug.App):
    def __init__(self, song):
        super().__init__()
        self.song = song
    
    def appStarted(self):
        self.time = 0
        self.seconds = 0
        self.timerDelay = 100 # milliseconds

        self.gameOver = False

        # SONG LENGTH

        self.songLen = lenSong.AudioObject(song).lengthInSecs

        # PITCH

        self.pitchPath = pmp.PitchPath(song)
        self.path = self.pitchPath.getPitchPath() # Dictionary of frames to pitch
        self.frames = self.pitchPath.totalFrames # Total frames in pitchPath
        self.range = self.pitchPath.getPitchRange() # Range of pitches
        self.minPitch = self.pitchPath.getMinPitch() # Lowest pitch

        self.pitchPath = [] # Path of (x,y) based on (frame, pitch)
        self.xVals = []
        self.yVals = []
        for time in self.path:
            pitch = self.path[time]
            yVal = self.height//3 + ((pitch-self.minPitch)/self.range)*(self.height//3)
            xVal = time
            self.xVals.append(xVal)
            self.yVals.append(yVal)
            self.pitchPath.append((xVal, yVal))

        # Manually add last values of song, so that function never goes out of range
        lastVal = self.pitchPath[-1][1]
        self.xVals.append(self.songLen)
        self.yVals.append(lastVal)
        self.pitchPath.append((self.songLen, lastVal))

        x = self.xVals
        y = self.yVals
        self.f = interp1d(x, y, kind='cubic')
#        plt.plot(x, y, 'o', x, self.f(x), '-')
#        plt.show()

        # BEATS

        self.beatObj = bP.Beats(song)
        self.beats = self.beatObj.getBeats()
        self.beatVals = self.beatObj.roundToFirstDecimal()

        self.color = 'red'

        # BPM
        self.bpm = self.beatObj.convertBeatsToBPM()

        # PLAYER
        self.player = player.Player(self.width//4, self.height//2)
        self.attack = False
        self.injured = False

        # MOVEMENT
        self.scrollX = 0 # Scroll x value
        self.dx = self.bpm / 30 # 'Speed' based on bpm (avg 60)

        # PROJECTILE
        self.dpx = self.dx*6
        self.timeToReachPlayer = (self.width - self.player.x) / (self.dpx/0.1) # In seconds
        self.timeToReachPlayer = PitchPathmaker.roundToOneDecimal(self.timeToReachPlayer) # Round
        self.projectileYTime = self.timeToReachPlayer * 10 # Convert to 0.1 seconds (100 ms)
        self.projectile = False
        self.startProj = -1
        self.pr = 20
        self.px = self.width
        self.py = self.height//2
        self.finalY = None # Final y position, to match with player on the beat
        self.dpy = 0 # Initial y velocity
        self.apy = 2 # "Gravity"; i.e. acceleration of projectile in y-direction (APY)

        # BACKGROUND
        self.length = self.dx * (self.songLen/0.1)

    @staticmethod
    def roundToOneDecimal(n):
        val = int(n)
        decimals = (n - val)*10
        append = int(round(decimals))/10
        val += append
        return val

    def keyPressed(self, event):
        if (event.key == 'a'):
            s = self.seconds
            secondsRange = {s, s+0.1, s-0.1, s+0.2, s-0.2}
            if (secondsRange & self.beatVals != {}): # Set intersection for leniency
                self.attack = True
                self.player.attack()
        # If player hits 'a' on/around the beat (hits projectile), they turn green and gain 10 points

    def keyReleased(self, event):
        if (event.key == 'a'):
            if (self.attack):
                self.attack = False
                self.player.reset()

    def timerFired(self):
        self.seconds = PitchPathmaker.roundToOneDecimal(self.seconds)

        if not self.gameOver:
            if (self.seconds >= self.songLen):
                    self.gameOver = True
                    return 0                

            # Move axis/background back
            self.scrollX += self.dx
            # Adjust player y value according to pitch
            self.player.y = self.f(self.seconds)

            if (self.injured):
                self.player.reset()
                self.injured = False

            # Moving the projectile
            if (self.projectile):
                self.px -= self.dpx # Movement in x direction
                self.py += self.dpy # Movement in y direction
                self.dpy += self.apy # Acceleration downwards (y)
# POST MVP:     If projectile goes above canvas, tell the player (?)

                if (self.circlesOverlap()):
                    # 1. Either player attacks or is injured
                        # Attacks are covered in keyPressed
                    if (not self.attack):
                        self.injured = True
                        self.player.injured()
                        if (self.player.health <= 0):
                            self.gameOver = True
                            return 0 # Exit function
                    # 2. Collision occurred: reset & remove projectile
                    self.projectile = False
                    self.px = self.width
                    self.py = self.height//2

            # Initializing the projectile
            if (not self.projectile):
                self.startProj = self.seconds + self.timeToReachPlayer # Time at which projectile would hit player
                if (self.startProj in self.beatVals): # Is this time in beats?
                    self.projectile = True
                    self.finalY = self.f(self.startProj)
                    self.dpy = ( (self.finalY - self.py) - (1/2) * (self.apy * (self.projectileYTime**2) ) ) / self.projectileYTime

            self.seconds += 0.1 # 100 milliseconds => 0.1 second

    def circlesOverlap(self):
        x = self.player.x
        y = self.player.y
        # Player: x, y, r
        # Projectile: px, py, pr
        dx = (x - self.px)
        dy = (y - self.py)
        if (dx**2 + dy**2)**0.5 <= (self.player.r + self.pr):
            return True
        return False

    def redrawAll(self, canvas):
        if (not self.gameOver):
            # draw the x and y axes to start
            # scroll background, not characters
            ax = self.width/2 - self.scrollX
            ay = self.height/2
            canvas.create_line(ax, 0, ax, self.height)
            canvas.create_line(0, ay, self.width, ay)

            # draw 'player'
            x = self.player.x
            y = self.player.y
            r = self.player.r
            canvas.create_oval(x-r,y-r,x+r,y+r,fill=self.player.color)
            # draw player stats
            canvas.create_text(10, self.height-10, text = f'Health:{self.player.health}\tScore:{self.player.score}',anchor='sw')
            
            if (self.projectile):
                canvas.create_oval(self.px-self.pr,self.py-self.pr,self.px+self.pr,self.py+self.pr,fill='blue')

        else:
            canvas.create_text(self.width//2, self.height//2, text = 'Song Over')
            canvas.create_text(self.width//2, 2*self.height//3, text = f'SCORE: {self.player.score}')

mydir = r'C:\Users\Amy\15-112\termProject\TP1_Deliverable\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile
song = fileName
]
test = PitchPathmaker(song)