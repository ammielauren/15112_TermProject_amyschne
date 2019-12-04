# Written in separate file to keep main file less cluttered with classes
# No references, just basic class to track enemy and their properties

class Enemy(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y