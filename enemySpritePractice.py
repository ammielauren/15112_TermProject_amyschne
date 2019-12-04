from cmu_112_graphics import *
from tkinter import *
import os

# Reference for spritesheet/strip creation:
# http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#spritesheetsWithCropping

class EnemySprite(App):
    def appStarted(self):
        # Location: C:\Users\Amy\15-112\termProject\TP2_Deliverable
        # Name: spritesheet
        # Type: PNG File (.png)
        path = r'C:\Users\Amy\15-112\termProject\TP3_Deliverable\spritesheets\enemy_spritesheet.png'
        spritestrip = self.loadImage(path)
        self.sprites = []
        for i in range(6):
            # height: 0 - 200
            # width: i*200 + (i+1)*200
            sprite = spritestrip.crop((i*200, 0, (i+1)*200, 200))
            self.sprites.append(sprite)
        self.spriteCounter = 0

    def timerFired(self):
        self.spriteCounter = (1 + self.spriteCounter) % len(self.sprites)

    def redrawAll(self, canvas):
        sprite = self.sprites[self.spriteCounter]
        canvas.create_image(self.width//2, self.height//2, image=ImageTk.PhotoImage(sprite))

EnemySprite(width=400, height=400)