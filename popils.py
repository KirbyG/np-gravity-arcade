import pygame
import argparse

from popils_constants import *


# ----- Function definitions -----
# TODO 3sat to game state conversion function
def initSpecialAreas():
    playerRow = playerCol = 1
    assignmentRow = 2
    # initially set entire level to indestructible blocks
    # need 'for' because Python lists are "shallow"
    block_type = [[HARD] * COLS for row in range(ROWS)]

    # Starting zone
    block_type[playerRow][playerCol] = PLAYER
    for i in range(2, COLS - 2):
        block_type[playerRow][i] = SUPPORT
    block_type[playerRow][COLS - 2] = LADDER
    for i in range(1, COLS - 3, 2):
        block_type[assignmentRow][i] = SOFT
    block_type[assignmentRow][COLS - 2] = LADDER

    # Ending zone
    block_type[ROWS - 2][COLS - 2] = PRINCESS
    block_type[ROWS - 3][COLS - 2] = SOFT  # Stop princess from walking

    # send back partially-built level
    return block_type


def initSatisfiabilityClauses():
    global row_pointer
    VARS_PER_TUPLE = 3  # Definition of 3SAT

    for i in range(NUM_TUPLES):
        index = VARS_PER_TUPLE * i
        variable_states = [UNUSED] * NUM_VARS

        # Determine which variables were used in which clauses
        for j in range(VARS_PER_TUPLE):
            temp = array_form[index + j]
            # Map to -1, 0, or 1 (Negated, Absent, Present)
            variable_states[abs(temp) - 1] = int(abs(temp) / temp)
        place_gadget(variable_states, row_pointer)
        row_pointer += GADGET_HEIGHT


def place_gadget(variable_states, bottom_row):
    # Create transition to next zone
    state[bottom_row][COLS - 2] = LADDER
    state[bottom_row + 1][COLS - 2] = SUPPORT
    # state[bottom_row + 2][COLS - 2] is already HARD
    state[bottom_row + 3][COLS - 2] = LADDER
    state[bottom_row + 4][COLS - 2] = LADDER
    state[bottom_row + 5][COLS - 2] = LADDER

    # Carve out walkable area
    for i in range(2, COLS - 2, 2):
        state[bottom_row + 1][i] = SUPPORT
        state[bottom_row + 3][i] = SUPPORT
        state[bottom_row + 4][i] = SUPPORT

    # Place ladders according to gadget structure
    for i in range(len(variable_states)):
        place_sub_gadget(variable_states[i], bottom_row + 1, 2 * i + 1)


# Clone sub-gadget structure
def place_sub_gadget(code, bottom_row, col):
    for i in range(SUB_GADGET_HEIGHT):
        state[bottom_row + i][col] = SUB_GADGETS[code + 1][i]


# ----- Main program begins here -----
print()  # Give separation from pygame message

# read in 3SAT problem
parser = argparse.ArgumentParser()
input = parser.add_mutually_exclusive_group()
input.add_argument('-i', '--instance', nargs='+', type=str,
                   help="3SAT instance: (default = " + DEFAULT_3SAT + ")")
input.add_argument('-f', '--filename',
                   help="file containing an instance of 3SAT")
args = parser.parse_args()

# Currently these all just blindly accept the input they're given
# TODO Could make input more robust against typos
# TODO multiple 3sat instances stored in files
# TODO require all variable values in range to be used (e.g. prohibit only x1, x2, x7)
if args.instance:
    three_sat = " ".join(args.instance)
elif args.filename:
    with open(args.filename) as file:
        three_sat = file.readline()
else:
    three_sat = DEFAULT_3SAT

array_form = [int(el) for el in str.split(three_sat)]
truncation_needed = False
while len(array_form) % 3 != 0:
    array_form = array_form[:-1]
    truncation_needed = True
if truncation_needed:
    print("WARNING: 3SAT requires tuples of exactly size 3. Input has been truncated appropriately.")
print("3SAT instance: " + str(array_form))
# TODO print pretty version of 3SAT with proper formatting & symbols

# initialize all pygame submodules
pygame.init()

# window title
pygame.display.set_caption('Test')

clock = pygame.time.Clock()
window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
block_size = 50  # in px TODO dynamic block sizing

# initialize drawing surface
screen = pygame.display.set_mode(window_size)

# set up runtime constants
NUM_TUPLES = (len(array_form) / 3)
NUM_VARS = max([abs(el) for el in array_form])
ROWS = 6 * (NUM_TUPLES + 1)
COLS = 3 + 2 * NUM_VARS
BLOCK = min(window_size[1] / ROWS, window_size[0] / COLS)

# set up variables
row_pointer = 3
hidden = SUPPORT  # tile obscured by player position
redRow = 1
redCol = 1

# Create bottom 3 rows & top 2 rows of puzzle
# Remaining area, including frame, is made of HARD blocks
state = initSpecialAreas()

# Place gadgets to construct puzzle
initSatisfiabilityClauses()

# game loop
done = False
while done is False:  # TODO block breaking logic
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP:  # TODO functions!
            if event.key == pygame.K_LEFT and state[redRow][redCol - 1] != HARD:
                state[redRow][redCol] = hidden
                redCol = redCol - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = PLAYER
            elif event.key == pygame.K_RIGHT and state[redRow][redCol + 1] != HARD:
                state[redRow][redCol] = hidden
                redCol = redCol + 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = PLAYER
            elif event.key == pygame.K_UP:
                if state[redRow + 1][redCol] == SUPPORT or state[redRow + 1][redCol] == LADDER and hidden == LADDER:
                    state[redRow][redCol] = hidden
                    redRow = redRow + 1
                    hidden = state[redRow][redCol]
                    state[redRow][redCol] = PLAYER
                elif state[redRow + 1][redCol] == SOFT:
                    for falling_row in range(redRow + 1, rows - 1):
                        state[falling_row][redCol] = state[falling_row + 1][redCol]
                    state[rows - 1][redCol] = HARD
            elif event.key == pygame.K_DOWN and state[redRow - 1][redCol] != HARD:
                state[redRow][redCol] = hidden
                redRow = redRow - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = PLAYER
        while (state[redRow - 1][redCol] == SUPPORT and hidden == SUPPORT):
            state[redRow][redCol] = hidden
            redRow = redRow - 1
            hidden = state[redRow][redCol]
            state[redRow][redCol] = PLAYER
    screen.fill(BACKGROUND)
    # render
    for row in range(rows):
        for col in range(cols):
            pygame.draw.rect(screen, state[rows - row - 1][col],
                             [col * BLOCK + 1, row * BLOCK + 1, BLOCK - 1, BLOCK - 1])
    pygame.display.flip()
    clock.tick(20)
pygame.quit()
