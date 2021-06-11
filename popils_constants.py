# Types of blocks
PLAYER = (255, 0, 0)  # red
LADDER = (0, 0, 255)  # blue
HARD = (210, 180, 140)  # tan
SOFT = (128, 128, 128)  # gray
PRINCESS = (250, 20, 200)  # pink
SUPPORT = (255, 255, 255)  # white
BACKGROUND = (0, 0, 0)  # black
COLORS = (PLAYER, LADDER, HARD, SOFT, PRINCESS, SUPPORT)

# Possible variable states within a clause
NEGATED = -1
ABSENT = 0
PRESENT = 1

SUB_GADGET_NEGATED = [LADDER, LADDER, SUPPORT, LADDER]
SUB_GADGET_ABSENT = [LADDER, SUPPORT, LADDER, SUPPORT]
SUB_GADGET_PRESENT = [SUPPORT, LADDER, LADDER, SUPPORT]
SUB_GADGETS = [SUB_GADGET_NEGATED, SUB_GADGET_ABSENT, SUB_GADGET_PRESENT]

# Measured in block units
SUB_GADGET_HEIGHT = 4
GADGET_HEIGHT = 6

# Set up runtime constants
# NUM_VARS = max([abs(el) for el in array_form])
# ROWS = 6 * (NUM_TUPLES + 1)
# COLS = 3 + 2 * NUM_VARS
# BLOCK_DIM = min(WINDOW_HEIGHT / ROWS, WINDOW_WIDTH / COLS)


class Player:
    def __init__(self):
        self.occupying = SUPPORT
        self.row = 1
        self.col = 1
        self.color = PLAYER
