# Written in separate file to keep main file less cluttered with classes
# No references, just basic class to track player and their properties

class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 30
        self.score = 0
        self.health = 100
        self.attacking = False
        self.injury = False
    
    def attack(self):
        self.score += 10
        # Change sprite to attacking sprite
        self.attacking = True

    def injured(self):
        self.health -= 5
        # Change sprite to injured sprite
        self.injury = True
    
    def reset(self):
        self.attacking = False
        self.injury = False
        pass
        # Change sprite back to basic movement spritestrip