import random

class Projectile(object):
    def __init__(self, x, y, finalY, apy, yTime):
        self.x = x
        self.y = y
        self.r = 20
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        colorIndex = random.randint(0, 5)
        self.color = colors[colorIndex]
        self.finalY = finalY
        self.dpy = ( (self.finalY - self.y) - (1/2) * (apy * (yTime**2) ) ) / yTime
