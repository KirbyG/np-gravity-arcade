from enum import Enum

# Colors of blocks
# TODO: Make Block class with label/color attributes?
PLAYER = (255, 0, 0)  # red
LADDER = (0, 0, 255)  # blue
HARD = (210, 180, 140)  # tan
SOFT = (128, 128, 128)  # gray
PRINCESS = (250, 20, 150)  # pink
SUPPORT = (255, 255, 255)  # white
BACKGROUND = (0, 0, 0)  # black

ROW = 1
COL = 0


class VariableState(Enum):
    UNUSED = 0
    NEGATED = -1
    NONNEGATED = 1
