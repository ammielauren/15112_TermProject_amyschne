from cmu_112_graphics import *
import module_manager
import sidescroller
module_manager.review()

#################################################
# CHARACTERS
#################################################

class NonPlayable(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Throws projectiles & rushes toward Player (defeated with many hits)
class Boss(NonPlayable):
    def __init__(self, x, y, power, strength):
        # power = damage given each hit
        # strength = max damage taken
        super().__init__()
        self.power = power
        self.strength = strength

    def attack(self):
        # throw projectile SMARTLY
        pass

    def move(self):
        # move left
        # recursively / algorithmically
        # follow character around map
        pass

# Hover wherever they are
class Enemy(NonPlayable):
    def __init__(self, x, y):
        super().__init__()
        # determine type from pitch of beat
        # high => high enemy; low => low enemy        

class Buddy(NonPlayable):
    def attack(self):
        pass
    def die(self):
        pass

class Player(object):
    def __init__(self, x, y, image):
        # Positioning
        self.x = x
        self.y = y
        self.scrollX = 0
        self.moving = True
        # Scoring
        self.score = 0
        self.scoreStreak = False
        # Image
        self.image = image # URL, load in GameMode
        self.sprites = []

#################################################
# OBJECTS
#################################################

class Item(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dy = 1

class Obstacle(Item):
    pass
    # create on off beats

class Projectile(Item):
    def fall(self):
        self.y -= self.dy
        # Call in TIMERFIRED
        # Calculate timing:
        #   COLLISION with PLAYER occurs on BEAT

#################################################
# LEVELS, BACKGROUNDS
#################################################

# Consider how backgrounds & pathways will be implemented in sidescroller
# Backgrounds:  drawn like dots but more complicated
# Paths:        directional

#################################################
# GAME MODES
#################################################

class GameMode(Mode):
    def appStarted(self):

        self.gameOver = False
        mode.player = Player(0,0)

        x = self.width
        y = self.height
        self.lowHeight = 2*y//3
        self.highHeight = y//3

        self.enemy = Enemy(x, self.lowHeight)
