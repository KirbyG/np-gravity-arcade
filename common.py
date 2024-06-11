import numpy as np

# Definition of 3SAT
VARS_PER_CLAUSE = 3

# BLOCK TYPES
COMMON = 0 * 10
POPILS = 1 * 10
MEGALIT = 2 * 10

PLAYER = COMMON + 0
AIR = COMMON + 1

LADDER = POPILS + 0
HARD = POPILS + 1
BREAKABLE = POPILS + 2
PRINCESS = POPILS + 3

BORDER = MEGALIT + 0
ROCKBOTTOM = MEGALIT + 1
ROCKTOP = MEGALIT + 2
ROCKLEFT = MEGALIT + 3
ROCKRIGHT = MEGALIT + 4
ROCKCOLUMN = MEGALIT + 5
ROCKROW = MEGALIT + 6
ROCKPOINT = MEGALIT + 7

JUGS = [ROCKBOTTOM, ROCKLEFT, ROCKRIGHT]

ROCKS = [ROCKBOTTOM, ROCKTOP, ROCKLEFT, ROCKRIGHT, ROCKCOLUMN, ROCKROW, ROCKPOINT]

# COLORS for each block. ROCK types differ in shape to render shapes of slabs
COLORS = {
    PLAYER: (255, 0, 0),
    AIR: (255, 255, 255),
    LADDER: (0, 0, 255),
    HARD: (210, 180, 140),
    BREAKABLE: (128, 128, 128),
    PRINCESS: (250, 20, 200),
    BORDER: (0, 200, 0),
}
COLORS.update((ROCK, (50, 50, 50)) for ROCK in ROCKS)

# purely mathematical helper function mapping -R -> -1, R -> 1
def sign(num):
    return 0 if not num else int(abs(num) / num)

LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])
UP = np.array([0, 1])
DOWN = np.array([0, -1])
ZERO = np.array([0, 0])

# this is sugar for using a 2-vector to index a matrix
_ = tuple

# less cancerous sugar
X = 0
Y = 1

# https://stackoverflow.com/questions/1986152/why-doesnt-python-have-a-sign-function
import math
sign = lambda x: math.copysign(1, x)