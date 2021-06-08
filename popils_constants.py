# in px
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 1000

# Types of blocks
PLAYER = (255, 0, 0)  # red
LADDER = (0, 0, 255)  # blue
HARD = (210, 180, 140)  # tan
SOFT = (128, 128, 128)  # gray
PRINCESS = (250, 20, 200)  # pink
SUPPORT = (255, 255, 255)  # white
BACKGROUND = (0, 0, 0)  # black
COLORS = (PLAYER, LADDER, HARD, SOFT, PRINCESS, SUPPORT)

SUB_GADGET_UNUSED = [LADDER, SUPPORT, LADDER, SUPPORT]
SUB_GADGET_NEGATED = [LADDER, LADDER, SUPPORT, LADDER]
SUB_GADGET_NONNEGATED = [SUPPORT, LADDER, LADDER, SUPPORT]
SUB_GADGETS = [SUB_GADGET_UNUSED, SUB_GADGET_NEGATED, SUB_GADGET_NONNEGATED]

GADGET_UNUSED = [LADDER, SUPPORT, LADDER, SUPPORT]
GADGET_NEGATED = [LADDER, LADDER, SUPPORT, LADDER]
GADGET_NONNEGATED = [SUPPORT, LADDER, LADDER, SUPPORT]
SUB_GADGETS = [GADGET_NEGATED, GADGET_UNUSED, GADGET_NONNEGATED]

# in block units
SUB_GADGET_HEIGHT = 4
GADGET_HEIGHT = 6

# default 3SAT instance. Will be ignored if user provides alternative
DEFAULT_3SAT = '1 2 3 -2 -3 4 1 -3 6 -1 4 5 2 -4 -6'

UNUSED = 0
NEGATED = -1
NONNEGATED = 1

# DIRECTIONS
LEFT = [0, -1]
RIGHT = [0, 1]
UP = [1, 0]
DOWN = [-1, 0]
