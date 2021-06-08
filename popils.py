import pygame
import argparse

from popils_constants import *


# ----- Function definitions -----
# TODO 3sat to game state conversion function
def initSpecialAreas():
    playerRow = playerCol = 1
    assignmentRow = 2
    # Initially set entire level to indestructible blocks
    # Need 'for' in secodn dimension because Python lists are "shallow"
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

    # Send back partially-built level
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
            variable_states[abs(temp) - 1] = sign(temp)
        place_gadget(variable_states, row_pointer)
        row_pointer += GADGET_HEIGHT


def sign(num):
    return int(abs(num) / num)


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


def move(vector):
    global state, hidden, redRow, redCol, fresh

    if vector == UP and state[redRow + 1][redCol] == SOFT:
        fresh = False

    else:
        state[redRow][redCol] = hidden
        redRow = redRow + vector[0]
        redCol = redCol + vector[1]
        hidden = state[redRow][redCol]
        state[redRow][redCol] = PLAYER
        draw(min(redRow, redRow - vector[0]), max(redRow, redRow - vector[0]),
             min(redCol, redCol - vector[1]), max(redCol, redCol - vector[1]))


def force(vector):
    global state, hidden, redRow, redCol, fresh
    target = state[redRow + vector[0]][redCol + vector[1]]
    if vector == UP:
        if target == SOFT:
            fresh = False
            for falling_row in range(redRow + 1, ROWS - 1):
                state[falling_row][redCol] = state[falling_row + 1][redCol]
            state[ROWS - 1][redCol] = HARD
            draw(redRow + 1, ROWS - 1, redCol, redCol)
        elif hidden == LADDER and (target != HARD):
            move(UP)
    elif target != HARD:
        move(vector)


def passes(var, guess):
    return sign(var) * guess[abs(var) - 1] == 1


def draw(min_row, max_row, min_col, max_col):
    global state, screen
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            pygame.draw.rect(screen, state[row][col],
                             [col * BLOCK + 1, (ROWS - row - 1) * BLOCK + 1, BLOCK - 1, BLOCK - 1])
    pygame.display.update()


def renderDisplay():
    screen.fill(BACKGROUND)
    for row in range(ROWS):
        # Create a rect for each block according to its saved state/color
        for col in range(COLS):
            pygame.draw.rect(screen, state[ROWS - row - 1][col],
                             [col * BLOCK + 1, row * BLOCK + 1, BLOCK - 1, BLOCK - 1])
    pygame.display.flip()  # Update visual surface (i.e. the entire display)


# ----- Main program begins here -----
print()  # Give separation from pygame message

# Read in 3SAT problem
parser = argparse.ArgumentParser()
input_type = parser.add_mutually_exclusive_group()
input_type.add_argument('-i', metavar='VAR', dest='instance', nargs='*',
                        type=str, help="1 2 -3 is equivalent to the clause (x1 || x2 || !x3). Default is " + DEFAULT_3SAT)
input_type.add_argument('-f', dest='filename',
                        help="file containing an instance of 3SAT")
parser.add_argument('-s', dest='--solver', action='store_true',
                    help='run puzzle auto-solver')
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
# TODO print pretty version of 3SAT in conjunctive normal form

# Initialize all pygame submodules
pygame.init()

# Set window title
pygame.display.set_caption('Test')

clock = pygame.time.Clock()
window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
block_size = 50  # in px TODO dynamic block sizing

# Initialize drawing surface
screen = pygame.display.set_mode(window_size)

# set player position
hidden = SUPPORT

# Set up runtime constants
NUM_TUPLES = int(len(array_form) / 3)
NUM_VARS = max([abs(el) for el in array_form])
ROWS = 6 * (NUM_TUPLES + 1)
COLS = 3 + 2 * NUM_VARS
BLOCK = min(WINDOW_HEIGHT / ROWS, WINDOW_WIDTH / COLS)

# Set up variables
row_pointer = 3
nested_form = [[array_form[3 * i + j]
                for j in range(3)] for i in range(NUM_TUPLES)]

done = False
fresh = True
solution = []
autosolve = -1

redRow = 1
redCol = 1

# Create bottom 3 rows & top 2 rows of puzzle
# Remaining area, including frame, is made of HARD blocks
state = initSpecialAreas()

# Place gadgets to construct puzzle
initSatisfiabilityClauses()

draw(0, ROWS - 1, 0, COLS - 1)

while done is False:
    if autosolve > -1:
        force(solution[autosolve])
        autosolve = autosolve + 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        else:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    force(LEFT)
                elif event.key == pygame.K_RIGHT:
                    force(RIGHT)
                elif event.key == pygame.K_UP:
                    force(UP)
                elif event.key == pygame.K_DOWN and state[redRow - 1][redCol] != HARD:
                    force(DOWN)
        while (state[redRow - 1][redCol] == SUPPORT and hidden == SUPPORT):
            force(DOWN)
    if fresh and redRow == 1 and redCol == 1 and event.type == pygame.KEYUP and event.key == pygame.K_a:
        # autosolve
        autosolve = 0
        # compute vector sequence
        # find the solving variable assignment by brute force
        good_guess = []
        for guess in range(2 ** NUM_VARS):
            form = r'{:0' + str(NUM_VARS) + r'b}'
            parsed_guess = [int(form.format(guess)[j]) *
                            2 - 1 for j in range(NUM_VARS)]
            solve = True
            for clause in range(NUM_TUPLES):
                satisfied = False
                for var in range(3):
                    temp = nested_form[clause][var]
                    if passes(temp, parsed_guess):
                        satisfied = True
                        parsed_guess
                if satisfied is False:
                    solve = False
                    break
            if solve:
                good_guess = parsed_guess
        if len(good_guess) == 0:
            done = True
        else:
            # set variables
            for var in good_guess:
                if var == 1:
                    solution.append(UP)
                solution.append(RIGHT)
                solution.append(RIGHT)
            # traverse level
            for tuple in range(NUM_TUPLES):
                solution.append(UP)
                solution.append(UP)
                solution.append(UP)
                shuffle = 2 * (11 - max([abs(nested_form[tuple][var])
                               for var in range(3) if passes(nested_form[tuple][var], good_guess)]))
                for i in range(shuffle):
                    solution.append(LEFT)
                solution.append(UP)
                solution.append(UP)
                for i in range(shuffle):
                    solution.append(RIGHT)
                solution.append(UP)
            solution.append(UP)
            solution.append(UP)
            solution.append(UP)
    clock.tick(20)
    renderDisplay()
pygame.quit()
