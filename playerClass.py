class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 30
        self.color = 'blue'
        self.score = 0
        self.health = 100
    
    def attack(self):
        self.score += 10
        self.color = 'green'

    def injured(self):
        self.health -= 10
        self.color = 'red'
    
    def reset(self):
        self.color = 'blue'