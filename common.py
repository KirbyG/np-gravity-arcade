import numpy as np

# Definition of 3SAT
VARS_PER_CLAUSE = 3

# colors named based on in-game functionality
COLORS = {
    'ladder': (0, 0, 255),
    'hard': (210, 180, 140),
    'breakable': (128, 128, 128),
    'princess': (250, 20, 200),
    'support': (255, 255, 255),
    'air': (255, 255, 255),
    'slab': (128, 128, 128),
    'border': (0, 200, 0),
    'tip':  (128, 128, 128),
    'gripped': (50, 50, 50),
    'background': (0, 0, 0),
    'player': (255, 0, 0),
}

# purely mathematical helper function mapping -R -> -1, R -> 1
def sign(num):
    return 0 if not num else int(abs(num) / num)

LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])
UP = np.array([0, 1])
DOWN = np.array([0, -1])
ZERO = np.array([0, 0])

# this is sugar
_ = tuple
# less cancerous sugar
X = 0
Y = 1