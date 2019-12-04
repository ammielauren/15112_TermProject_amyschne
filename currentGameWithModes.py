import lengthOfSong as lenSong
import pathmakerPitch as pmp
import beatsParser as bP
import playerClass as player
import enemyClass as eC
import cmu_112_graphics as cmug
from cmu_112_graphics import *
from tkinter import *
import os
from scipy.interpolate import interp1d
import projectileClass as pC
import winsound

import random

# References:

# Scipy Interpolation Documentation: https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html#d-interpolation-interp1d
# CMU Graphics:
    # Animation Framework:
        # http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
    # cmu_112_graphics source:
        # http://www.cs.cmu.edu/~112/notes/hw7.html
# Spritesheet/strip creation and cycling:
    # http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#spritesheetsWithCropping
# Mode references:
    # http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#subclassingModalApp
    # http://www.cs.cmu.edu/~112/notes/hw9.html
    # hw9 assignment/experience
# Custom colors:
    # http://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html#customColors
# Audio .wav sample files:
    # https://file-examples.com/index.php/sample-audio-files/sample-wav-download/
    # Artist: Kevin MacLoed
# Playing audio simultaneously as game runs:
    # https://stackoverflow.com/questions/44472162/how-do-play-audio-playsound-in-background-of-python-script
    # https://docs.python.org/2/library/winsound.html

class PitchPathmaker(cmug.Mode):
    
    def appStarted(self):
        # TIME
        self.time = 0
        self.seconds = 0
        self.timerDelay = 100 # milliseconds

        # GENERAL THINGS
        self.gameOver = False
        self.gameStarted = False
        self.msg = None
        mydir = r'C:\Users\Amy\15-112\termProject\TP3_Deliverable\sampleAudio'
        file1 = mydir + os.sep + 'file_example_WAV_1MG.wav'
        file2 = mydir + os.sep + 'file_example_WAV_10MG.wav'
        file3 = mydir + os.sep + 'file_example_WAV_2MG.wav'
        self.files = [file1, file2, file3]
        self.song = None

        # CHOOSING SONG - DRAW
        self.margin = 20
        self.rSize = (self.width - 4*self.margin)//3
        self.rY1 = 2*self.height//3 + self.margin
        self.rY2 = 2*self.height//3 + 3*self.margin

        # PLAYER
        self.player = player.Player(self.width//4, self.height//2)
        self.attack = False
        self.attackRange = set()
        self.injured = False
        self.scoreStreak = 0
        self.bestScorestreak = 0

        # PLAYER SPRITE
        path = r'C:\Users\Amy\15-112\termProject\TP3_Deliverable\spritesheets\player1_spritesheet.png'
        spritestrip = self.loadImage(path)
        self.sprites = []
        for i in range(8):
            # height: 0 - 200
            # width: i*200 + (i+1)*200
            bigSprite = spritestrip.crop((i*200, 0, (i+1)*200, 200))
            sprite = self.scaleImage(bigSprite, 1/2)
            sDims = sprite.size
            self.sprites.append(sprite)
        self.spriteCounter = 0
        self.r = (sDims[0]**2 + sDims[1]**2)**0.5 // 2
        self.playerAttackingSprite = self.loadImage(r'C:\Users\Amy\15-112\termProject\TP3_Deliverable\spritesheets\attackingSprite.png')
        self.attackSprite = self.scaleImage(self.playerAttackingSprite, 1/2)
        self.playerInjurySprite = self.loadImage(r'C:\Users\Amy\15-112\termProject\TP3_Deliverable\spritesheets\injuredSprite.png')
        self.injuredSprite = self.scaleImage(self.playerInjurySprite, 1/2)

        # ENEMY SPRITE
        self.throwing = False
        enemyPath = r'C:\Users\Amy\15-112\termProject\TP3_Deliverable\spritesheets\enemy_spritesheet.png'
        enemySpritestrip = self.loadImage(enemyPath)
        self.enemySprites = []
        for i in range(6):
            # height: 0 - 200
            # width: i*200 + (i+1)*200
            bigSprite = enemySpritestrip.crop((i*200, 0, (i+1)*200, 200))
            sprite = self.scaleImage(bigSprite, 1/2)
            eDims = sprite.size
            self.enemySprites.append(sprite)
        self.enemyXSize = sprite.size[0]
        self.enemyYSize = sprite.size[1]
        self.enemySpriteCounter = 0

        # BACKGROUND
        backgroundPath = r'C:\Users\Amy\15-112\termProject\TP3_Deliverable\spritesheets\longPlainBlackBackground.png'
        backgroundStrip = self.loadImage(backgroundPath)
        if (backgroundStrip.size[1] < self.height):
            scaleFactor = self.height//backgroundStrip.size[1]
            self.fullBackground = self.scaleImage(backgroundStrip, scaleFactor)
        else:
            self.fullBackground = backgroundStrip
        self.currentBackground = self.fullBackground.crop((0, 0, self.width, self.height))
        self.backgroundXSize = self.fullBackground.size[0]

    def setAudioValues(self, song):
        self.song = song

        # SONG LENGTH
        self.songLen = lenSong.AudioObject(self.song).lengthInSecs

        # BEATS
        self.beatObj = bP.Beats(self.song)
        self.beats = self.beatObj.getBeats()
        self.beatVals = self.beatObj.roundToFirstDecimal()

        # BPM
        self.bpm = self.beatObj.convertBeatsToBPM()

        # MOVEMENT
        self.scrollX = 0 # Scroll x value
        self.dx = self.bpm / 10 # 'Speed' based on bpm (avg 60)

        # BACKGROUND
        self.length = self.dx * (self.songLen/0.1)

        # PITCH
        self.pitchPath = pmp.PitchPath(self.song)
        self.path = self.pitchPath.getPitchPath() # Dictionary of frames to pitch
        self.frames = self.pitchPath.totalFrames # Total frames in pitchPath
        self.range = self.pitchPath.getPitchRange() # Range of pitches
        self.minPitch = self.pitchPath.getMinPitch() # Lowest pitch

        self.pitchPath = [(0, self.height//2)] # Path of (x,y) based on (frame, pitch)
        self.curvePathVals = [(self.width//4, self.height//2)] # Path of (x, y) based on (scrollX, height)
        self.xVals = []
        self.yVals = []
        for time in self.path:
            pitch = self.path[time]
            yVal = self.height//4 + ((pitch-self.minPitch)/self.range)*(self.height//2) # Scale y value by pitch, relative to range of pitches
            xVal = time
            xValForCurve = (self.dx * time * 10) + self.width//4
            self.xVals.append(xVal)
            self.yVals.append(yVal)
            self.pitchPath.append((xVal, yVal))
            self.curvePathVals.append((xValForCurve, yVal))

        # Manually add last values of song
        # Therefore function never goes out of range while song is still going
        lastVal = self.pitchPath[-1][1]
        self.xVals.append(self.songLen)
        self.yVals.append(lastVal)
        self.pitchPath.append((self.songLen, lastVal))
        self.curvePathVals.append((self.length, lastVal))
        self.curvePath = tuple(self.curvePathVals)

        x = self.xVals
        y = self.yVals
        self.f = interp1d(x, y, kind='cubic')

        # ENEMY
        self.enemy = eC.Enemy(self.width-100, self.height//2)
        ex = self.enemy.x
        ey = self.enemy.y

        # PROJECTILE
        self.projectiles = []
        self.dpx = self.dx*2
        self.timeToReachPlayer = ((self.width-self.enemyXSize) - self.player.x) / (self.dpx/0.1) # In seconds
        self.timeToReachPlayer = PitchPathmaker.roundToOneDecimal(self.timeToReachPlayer) # Round
        self.projectileYTime = self.timeToReachPlayer * 10 # Convert to 0.1 seconds (100 ms)

        self.apy = 1 # "Gravity"; i.e. acceleration of projectile in y-direction (APY)

        winsound.PlaySound(self.song, winsound.SND_ASYNC | winsound.SND_ALIAS)

    @staticmethod
    def roundToOneDecimal(n):
        val = int(n)
        decimals = (n - val)*10
        append = int(round(decimals))/10
        val += append
        return val

    def keyReleased(self, event):
        if (event.key == 'Space'):
            self.attack = False

    # Currently, any key to attack
    def keyPressed(self, event):
        if (event.key == 'h'):
            self.app.setActiveMode(self.app.helpMode)
        elif (event.key == 'Space'):
            self.attack = True
            s1 = self.seconds
            s2 = PitchPathmaker.roundToOneDecimal(s1 + 0.1)
            s3 = PitchPathmaker.roundToOneDecimal(s1 - 0.1)
            self.attackRange = {s1, s2, s3}
            self.player.attacking = True
        elif (event.key == 'r'):
            self.appStarted()
            self.app.setActiveMode(self.app.splashScreenMode)
        elif (event.key == 'S'):
            self.app.setActiveMode(self.app.bigHelpMode)

    def playerProjectileIntersection(self):
        # LOOP THROUGH PROJECTILES
        for projectile in self.projectiles:
            px = projectile.x
            py = projectile.y
            x = self.player.x
            y = self.player.y
            # Player: x, y
            # Projectile: px, py, pr
            dx = x - px
            dy = y - py
            d = ((dx**2) + (dy**2))**0.5
            if (d <= self.r + projectile.r):
                return projectile
        return None

    def timerFired(self):

        if (not self.gameOver and self.gameStarted):
            self.seconds = PitchPathmaker.roundToOneDecimal(self.seconds)
            # Check if song is over
            if (self.seconds >= self.songLen):
                    self.gameOver = True
                    winsound.PlaySound(None, winsound.SND_ASYNC)
                    return 0

            # Reset message every second
            if (self.seconds % 1 == 0):
                self.msg = None

            # Cycle player sprites
            self.spriteCounter = (1 + self.spriteCounter) % len(self.sprites)

            # Cycle enemy sprites if throwing
            if (self.throwing):
                self.enemySpriteCounter = (1 + self.enemySpriteCounter) % len(self.enemySprites)
            else:
                self.enemySpriteCounter = 0
            
            # Move axis/background/curve back
            self.scrollX += self.dx

            for i in range(len(self.curvePathVals)):
                pair = self.curvePathVals[i]
                # Reassign curve, pushing back the x value by the scroll
                newPair = (pair[0] - (self.dx), pair[1])
                self.curvePathVals[i] = newPair
            self.curvePath = tuple(self.curvePathVals) # Reassign curve path

            backgroundScroll = self.scrollX % self.backgroundXSize
            self.currentBackground = self.fullBackground.crop((backgroundScroll, 0, self.width + backgroundScroll, self.height))
 
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
                    if (self.seconds in self.attackRange):
                        # Account for attack
                        self.player.attack()
                        self.msg = f'New score: {self.player.score}'
                        # Account for scorestreak
                        self.scoreStreak += 1
                        if (self.scoreStreak > self.bestScorestreak):
                            self.msg = f'New best scorestreak! {self.bestScorestreak}'
                            self.bestScorestreak = self.scoreStreak
                        self.attackRange = set()
                    else:
                        # Account for injury
                        self.injured = True
                        self.player.injured()
                        # Account for scorestreak
                        self.scoreStreak = 0
                        self.msg = f'Oh no! Your health decreased to {self.player.health}'
                        if (self.player.health <= 0):
                            self.gameOver = True
                            winsound.PlaySound(None, winsound.SND_ASYNC)
                            return 0 # Exit function
                    # 2. Collision occurred: remove projectile
                    self.projectiles.remove(projectile)
            
            # Initializing the projectile
            startProj = self.seconds + self.timeToReachPlayer # Time at which projectile would hit player
            if (startProj in self.beatVals): # Is this time in beats?
                finalY = self.f(startProj)
                # New projectile initialized
                newProjectile = pC.Projectile(self.width-self.enemyXSize, self.height//2, finalY, self.apy, self.projectileYTime)
                # New projectile added to list
                self.projectiles.append(newProjectile)
                self.throwing = True

            # Initialize enemy to throw projectile
            enemyStart = self.seconds + self.timeToReachPlayer
            if (enemyStart in self.beatVals):
                self.throwing = True

            self.seconds += 0.1 # 100 milliseconds => 0.1 second

    def mousePressed(self, event):
        if (not self.gameStarted):
            # Check which box click is in
            mx = event.x
            my = event.y
            box1 = ((self.margin, self.rY1), (self.margin+self.rSize, self.rY2))
            box2 = ((2*self.margin + self.rSize, self.rY1), (2*self.margin + 2*self.rSize, self.rY2))
            box3 = ((3*self.margin + 2*self.rSize, self.rY1), (3*self.margin + 3*self.rSize, self.rY2))
            # Check y value:
            if (my <= self.rY2 and my >= self.rY1):
                if (mx <= box1[1][0] and mx >= box1[0][0]): # In box1
                    song = self.files[0]
                    self.setAudioValues(song)
                    self.gameStarted = True
                elif (mx <= box2[1][0] and mx >= box2[0][0]): # In box2
                    song = self.files[1]
                    self.setAudioValues(song)
                    self.gameStarted = True
                elif (mx <= box3[1][0] and mx >= box3[0][0]): # In box3
                    song = self.files[2]
                    self.setAudioValues(song)
                    self.gameStarted = True

    # Custom color function from http://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html#customColors
    @staticmethod
    def rgbString(red, green, blue):
        # Don't worry about how this code works yet.
        return "#%02x%02x%02x" % (red, green, blue)

    def drawChoices(self, canvas):
        color0 = PitchPathmaker.rgbString(255, 205, 241)
        canvas.create_rectangle(0, 0, self.width, self.height, fill = color0)

        font = 'Arial 12'
        txt = 'Welcome to Melody in Motion!\nPick a song to start your game.'
        color1 = PitchPathmaker.rgbString(198, 196, 255)
        canvas.create_rectangle(self.margin, self.height//3, self.width-self.margin, 2*self.height//3, fill= color1)
        canvas.create_text(self.width//2, self.height//2, text=txt,font=font)

        color2 = PitchPathmaker.rgbString(255, 254, 205)
        canvas.create_rectangle(self.margin, self.rY1, self.margin + self.rSize, self.rY2, fill = color2)
        canvas.create_text((2*self.margin + self.rSize)//2, (self.rY1 + self.rY2)//2, text = 'Song 1')
        canvas.create_rectangle(2*self.margin + self.rSize, self.rY1, 2*self.margin + 2*self.rSize, self.rY2, fill = color2)
        canvas.create_text((4*self.margin + 3*self.rSize)//2, (self.rY1 + self.rY2)//2, text = 'Song 2')
        canvas.create_rectangle(3*self.margin + 2*self.rSize, self.rY1, 3*self.margin + 3*self.rSize, self.rY2, fill = color2)
        canvas.create_text((6*self.margin + 5*self.rSize)//2, (self.rY1 + self.rY2)//2, text = 'Song 3')

    def drawGame(self, canvas):
            # scroll background, not characters
            canvas.create_image(self.width//2, self.height//2, image = ImageTk.PhotoImage(self.currentBackground))
            # draw curve
            canvas.create_line(self.curvePath, fill = 'white', smooth = 1)

            # player position
            x = self.player.x
            y = self.player.y
            # draw sprite
            if (self.attack):
                canvas.create_image(x, y, image=ImageTk.PhotoImage(self.attackSprite))
            elif (self.injured):
                canvas.create_image(x, y, image=ImageTk.PhotoImage(self.injuredSprite))
            else:
                sprite = self.sprites[self.spriteCounter]
                canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))

            # write message in white box
            if (self.msg is not None):
                canvas.create_rectangle(self.width//2 - 50, self.height - 80, self.width//2 + 50, self.height-20, fill = 'white')
                canvas.create_text(self.width//2, self.height - 50, text = self.msg, width = 100)

            # draw player stats
            canvas.create_rectangle(10, self.height-75, 100, self.height-20, fill = 'pink')
            canvas.create_text(50, self.height-50, text = f'Health: {self.player.health}\nScore: {self.player.score}')

            # draw enemy
            ex = self.enemy.x
            ey = self.enemy.y
            enemySprite = self.enemySprites[self.enemySpriteCounter]
            canvas.create_image(ex, ey, image=ImageTk.PhotoImage(enemySprite))

            # draw projectiles
            for p in self.projectiles:
                canvas.create_oval(p.x-p.r, p.y-p.r, p.x+p.r, p.y+p.r, fill=p.color)

    def drawGameOver(self, canvas):
        # scroll background, not characters
        canvas.create_image(self.width//2, self.height//2, image = ImageTk.PhotoImage(self.currentBackground))
        # draw curve
        canvas.create_line(self.curvePath, fill = 'white', smooth = 1)
        if (self.player.health <= 0):
            text = f'Game over! You lost!\nHealth: 0\nScore: {self.player.score}\nBest streak: {self.bestScorestreak}'
        else:
            text = f'Game over! You win!\nYour score: {self.player.score}\nBest streak: {self.bestScorestreak}'
        canvas.create_text(self.width//2, self.height//2, text = text, fill = 'white')

    def redrawAll(self, canvas):
        if (not self.gameStarted):
            self.drawChoices(canvas)

        elif (not self.gameOver):
            self.drawGame(canvas)

        else:
            self.drawGameOver(canvas)

class SplashScreenMode(Mode):

    # Custom color function from http://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html#customColors
    @staticmethod
    def rgbString(red, green, blue):
        return "#%02x%02x%02x" % (red, green, blue)

    def redrawAll(self, canvas):
        frontColor = SplashScreenMode.rgbString(255, 205, 241)
        background = SplashScreenMode.rgbString(180, 178, 255)
        canvas.create_rectangle(0, 0, self.width, self.height, fill = background)
        canvas.create_rectangle(self.width//4, self.height//4, 3*self.width//4, 3*self.height//4, fill = frontColor)
        canvas.create_text(self.width//2, self.height//2, text = 'Welcome to Melody in Motion!\nClick to start.\nPress h for help if needed!')

    def mousePressed(self, event):
        self.app.setActiveMode(self.app.gameMode)

class HelpMode(Mode):
    def redrawAll(self, canvas):
        font = 'Arial 12'
        txt1 = 'Space to defend against enemy projectiles\nh for help\nr to return to game'
        canvas.create_rectangle(0,0,self.width,self.height,fill='pink')
        canvas.create_text(self.width/2,self.height/3,text=txt1,font=font)
    
    def keyPressed(self, event):
        if (event.key == 'r'):
            self.app.setActiveMode(self.app.gameMode)

class BigHelp(Mode):
    def redrawAll(self, canvas):
        font = 'Arial 12'
        txt = \
            '''
               Hello!
               This game is an audio-based sidescroller.
               It intakes an audio file (one of three, of the user's choosing),
               and creates a unique game experience using the Aubio module.

               The only control is 'Space' to attack. 'r' allows for restart.
               To exit this screen and restart the game, press 'g'.
               To exit this screen and restart the game, press 'r'.

               More details can be found in the ReadMe of the GitHub:
               https://github.com/ammielauren/15112_TermProject_amyschne/blob/master/README.md'''
        canvas.create_text(self.width//2, self.height//2, text = txt)

    def keyPressed(self, event):
        if (event.key == 'g'):
            self.app.setActiveMode(self.app.gameMode)
        elif (event.key == 'r'):
            self.app.setActiveMode(self.app.splashScreenMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.gameMode = PitchPathmaker()
        app.helpMode = HelpMode()
        app.bigHelpMode = BigHelp()
        app.setActiveMode(app.splashScreenMode)

def runApp():
    app = MyModalApp(width=600, height=400)

def main():
    runApp()

if __name__ == '__main__':
    main()

# Stop playing song if user closes app (when main stops running)
winsound.PlaySound(None, winsound.SND_ASYNC)