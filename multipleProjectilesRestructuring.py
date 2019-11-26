import lengthOfSong as lenSong
import pathmakerPitch as pmp
import beatsParser as bP
import playerClass as player
import cmu_112_graphics as cmug
from cmu_112_graphics import *
from tkinter import *
import os
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import projectileClass as pC

# References:

# Scipy Interpolation Documentation: https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html#d-interpolation-interp1d
# CMU Graphics:
    # Animation Framework:
        # http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
    # cmu_112_graphics source:
        # http://www.cs.cmu.edu/~112/notes/hw7.html
# Spritesheet/strip creation and cycling:
    # http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#spritesheetsWithCropping

class PitchPathmaker(cmug.App):
    def __init__(self, song):
        super().__init__()
        self.song = song
    
    def appStarted(self):

        # TIME
        self.time = 0
        self.seconds = 0
        self.timerDelay = 100 # milliseconds

        # GENERAL THINGS
        self.gameOver = False
        self.msg = None

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
            yVal = self.height//3 + ((pitch-self.minPitch)/self.range)*(self.height//3) # Scale y value by pitch, relative to range of pitches
            xVal = time
            self.xVals.append(xVal)
            self.yVals.append(yVal)
            self.pitchPath.append((xVal, yVal))

        # Manually add last values of song
        # Therefore function never goes out of range while song is still going
        lastVal = self.pitchPath[-1][1]
        self.xVals.append(self.songLen)
        self.yVals.append(lastVal)
        self.pitchPath.append((self.songLen, lastVal))

        x = self.xVals
        y = self.yVals
        self.f = interp1d(x, y, kind='cubic')

        # BEATS
        self.beatObj = bP.Beats(song)
        self.beats = self.beatObj.getBeats()
        self.beatVals = self.beatObj.roundToFirstDecimal()

        # BPM
        self.bpm = self.beatObj.convertBeatsToBPM()

        # PLAYER
        self.player = player.Player(self.width//4, self.height//2)
        self.attack = False
        self.injured = False
        # PLAYER SPRITE
        path = r'C:\Users\Amy\15-112\termProject\TP2_Deliverable\spritesheet_png.png'
        spritestrip = self.loadImage(path)
        self.sprites = []
        for i in range(4):
            # height: 0 - 200
            # width: i*200 + (i+1)*200
            bigSprite = spritestrip.crop((i*200, 0, (i+1)*200, 200))
            sprite = self.scaleImage(bigSprite, 1/2)
            sDims = sprite.size
            self.sprites.append(sprite)
        self.spriteCounter = 0
        self.r = (sDims[0]**2 + sDims[1]**2)**0.5 // 2

        # MOVEMENT
        self.scrollX = 0 # Scroll x value
        self.dx = self.bpm / 30 # 'Speed' based on bpm (avg 60)

        # PROJECTILE
        self.projectiles = []
        self.dpx = self.dx*6
        self.timeToReachPlayer = (self.width - self.player.x) / (self.dpx/0.1) # In seconds
        self.timeToReachPlayer = PitchPathmaker.roundToOneDecimal(self.timeToReachPlayer) # Round
        self.projectileYTime = self.timeToReachPlayer * 10 # Convert to 0.1 seconds (100 ms)

        self.apy = 2 # "Gravity"; i.e. acceleration of projectile in y-direction (APY)

        # BACKGROUND - for future implementation
        self.length = self.dx * (self.songLen/0.1)

    @staticmethod
    def roundToOneDecimal(n):
        val = int(n)
        decimals = (n - val)*10
        append = int(round(decimals))/10
        val += append
        return val

    # Currently, any key to attack
    def keyPressed(self, event):
        self.attack = True

    def playerProjectileIntersection(self):
        # LOOP THROUGH PROJECTILES
        for projectile in self.projectiles:
            # Player: x, y
            # Projectile: px, py, pr
            px = projectile.x
            py = projectile.y
            x = self.player.x
            y = self.player.y
            dx = x - px
            dy = y - py
            d = ((dx**2) + (dy**2))**0.5
            if (d <= self.r + projectile.r):
                return projectile
        return None # No projectile found to have collided with player

    def timerFired(self):

        self.seconds = PitchPathmaker.roundToOneDecimal(self.seconds)

        if not self.gameOver:
            # Check if song is over
            if (self.seconds >= self.songLen):
                    self.gameOver = True
                    return 0

            # Reset message every other second
            if (self.seconds % 2 == 0):
                self.msg = None

            # Cycle sprites
            self.spriteCounter = (1 + self.spriteCounter) % len(self.sprites)

            # Move axis/background back
            self.scrollX += self.dx
            # Adjust player y value according to pitch
            self.player.y = self.f(self.seconds)

            if (self.injured):
                self.player.reset()
                self.injured = False

            # Moving the projectile
            if (len(self.projectiles) > 0):
                for projectile in self.projectiles:
                    projectile.x -= self.dpx # Movement in x direction
                    projectile.y += projectile.dpy # Movement in y direction
                    projectile.dpy += self.apy # Acceleration downwards (y)

                if (self.playerProjectileIntersection() is not None): # Projectile collides with player
                    projectile = self.playerProjectileIntersection() # Returns projectile object that intersects with player
                    # 1. Either player attacks or is injured
                    if (not self.attack):
                        self.injured = True
                        self.player.injured()
                        self.msg = f'Oh no! Your health decreased to {self.player.health}'
                        if (self.player.health <= 0):
                            self.gameOver = True
                            return 0 # Exit function
                    else:
                        self.player.attack()
                        self.msg = f'New score: {self.player.score}'
                    # 2. Collision occurred: remove projectile
                    self.projectiles.remove(projectile)

            # Initializing the projectile
            startProj = self.seconds + self.timeToReachPlayer # Time at which projectile would hit player
            if (startProj in self.beatVals): # Is this time in beats?
                finalY = self.f(startProj)
                # Projectile motion equation for finding initial upwards velocity
                newProjectile = pC.Projectile(self.width, self.height//2, finalY, self.apy, self.projectileYTime)
                self.projectiles.append(newProjectile)

            self.seconds += 0.1 # 100 milliseconds => 0.1 second

    def keyReleased(self, event):
        self.attack = False

    def redrawAll(self, canvas):
        if (not self.gameOver):
            # draw the x and y axes to start
            # scroll background, not characters
            ax = self.width/2 - self.scrollX
            ay = self.height/2
            canvas.create_line(ax, 0, ax, self.height)
            canvas.create_line(0, ay, self.width, ay)

            # player position
            x = self.player.x
            y = self.player.y
            # draw sprite
            sprite = self.sprites[self.spriteCounter]
            canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))       
            if (self.msg is not None):
                canvas.create_text(self.width//2, self.height//3, text = self.msg)

            # draw player stats
            canvas.create_text(50, self.height-50, text = f'Health: {self.player.health}\tScore: {self.player.score}',anchor='sw')

            # draw projectiles
            for p in self.projectiles:
                canvas.create_oval(p.x-p.r, p.y-p.r, p.x+p.r, p.y+p.r, fill=p.color)

        else:
            canvas.create_text(self.width//2, self.height//2, text = 'Song Over')
            canvas.create_text(self.width//2, 2*self.height//3, text = f'SCORE: {self.player.score}\nHEALTH:{self.player.health}')

mydir = r'C:\Users\Amy\15-112\termProject\TP1_Deliverable\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile
song = fileName

test = PitchPathmaker(song)