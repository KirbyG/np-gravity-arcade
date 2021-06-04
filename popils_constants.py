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
COLORS = [PLAYER, LADDER, HARD, SOFT, PRINCESS, SUPPORT]

ROW = 1
COL = 0

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 1000

GADGET_UNUSED = [LADDER, SUPPORT, LADDER, SUPPORT]
GADGET_NEGATED = [LADDER, LADDER, SUPPORT, LADDER]
GADGET_NONNEGATED = [SUPPORT, LADDER, LADDER, SUPPORT]
SUB_GADGETS = [GADGET_UNUSED, GADGET_NEGATED, GADGET_NONNEGATED]
GADGET_HEIGHT = 4  # in block units

# default 3SAT instance. Will be ignored if user provides alternative
DEFAULT_3SAT = '9 7 2 6 4 1 8 7 3 -2 -4 -9 -7 -6 -1 -8 -3 -5 5 10 -10'


class VariableState(Enum):
    UNUSED = 0
    NEGATED = -1
    NONNEGATED = 1
