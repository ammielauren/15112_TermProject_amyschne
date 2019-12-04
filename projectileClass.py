import random

# References for projectile motion:
# https://courses.lumenlearning.com/physics/chapter/3-4-projectile-motion/
# https://www.khanacademy.org/science/physics/two-dimensional-motion/two-dimensional-projectile-mot/a/what-is-2d-projectile-motion

class Projectile(object):
    def __init__(self, x, y, finalY, apy, yTime, index):
        self.x = x
        self.y = y
        self.r = 20
        colors = ['pink', 'light blue', 'purple', 'light pink']
        self.color = colors[index]
        self.finalY = finalY
        self.dpy = ( (self.finalY - self.y) - (1/2) * (apy * (yTime**2) ) ) / yTime