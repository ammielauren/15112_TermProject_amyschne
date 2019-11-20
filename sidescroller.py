# SideScroller1:

from cmu_112_graphics import *
from tkinter import *
import random

import redrawPath

# Plan: Implement this into GameMode
# Use self.player.scrollX, etc.
# Design & add background, which will basically be drawn like the dots

class SideScroller1(App):
    def appStarted(self):
        self.scrollX = 0
        self.dots = [(random.randrange(self.width),
                      random.randrange(60, self.height)) for _ in range(50)]
        self.count = 0

    def keyPressed(self, event):
        # Add:
        # HIGH attack - w
        # LOW  attack - s
        # BOTH attack - w+s
        pass

    def timerFired(self):
        if (self.count % 5 == 0):
            self.dots.append((random.randrange(self.scrollX,self.width+self.scrollX), random.randrange(60, self.height)))
        self.count += 1
        self.scrollX += 5

    def redrawAll(self, canvas):
        # draw the dots, shifted by the scrollX offset
        r = 10
        for (x, y) in self.dots:
            x -= self.scrollX  # <-- This is where we scroll each dot!!!
            canvas.create_oval(x-r, y-r, x+r, y+r, fill='lightGreen')

        # draw the player fixed to the center of the scrolled canvas
        cx, cy, cr = self.width/4, self.height/2, 10
        canvas.create_oval(cx-cr, cy-cr, cx+cr, cy+cr, fill='cyan')

        # draw the x and y axes
        x = self.width/2 - self.scrollX # <-- This is where we scroll the axis!
        y = self.height/2
        canvas.create_line(x, 0, x, self.height)
        canvas.create_line(0, y, self.width, y)

        # draw the instructions and the current scrollX
        x = self.width/2
        canvas.create_text(x, 20, text='Use arrows to move left or right')
        canvas.create_text(x, 40, text=f'app.scrollX = {self.scrollX}')

SideScroller1(width=300, height=300)