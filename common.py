import numpy as np

# Definition of 3SAT
VARS_PER_CLAUSE = 3

# color codes
LADDER = 0
HARD = 1
BREAKABLE = 2
PRINCESS = 3
SUPPORT = 4
AIR = 5
SLAB = 6
BORDER = 7
TIP = 8
GRIPPED = 9
BACKGROUND = 10
PLAYER = 11

# colors named based on in-game functionality
COLORS = {
    LADDER: (0, 0, 255),
    HARD: (210, 180, 140),
    BREAKABLE: (128, 128, 128),
    PRINCESS: (250, 20, 200),
    SUPPORT: (255, 255, 255),
    AIR: (255, 255, 255),
    SLAB: (128, 128, 128),
    BORDER: (0, 200, 0),
    TIP:  (128, 128, 128),
    GRIPPED: (50, 50, 50),
    BACKGROUND: (0, 0, 0),
    PLAYER: (255, 0, 0),
}

# purely mathematical helper function mapping -R -> -1, R -> 1
def sign(num):
    return 0 if not num else int(abs(num) / num)

LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])
UP = np.array([0, 1])
DOWN = np.array([0, -1])
ZERO = np.array([0, 0])

# this is sugar for using a numpy vector to index a matrix
_ = tuple
# less cancerous sugar
X = 0
Y = 1