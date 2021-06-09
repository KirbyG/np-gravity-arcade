import pygame
import argparse

from popils_constants import *


# ----- Function definitions -----
def initSpecialAreas():
    playerRow = playerCol = 1
    assignmentRow = 2
    transitionCol = COLS - 2  # Column with path (ladders) between areas
    # Initially set entire zone to indestructible blocks
    # Using this "*" notation twice doesn't produce expected results
    #   because Python just makes pointers to original tuple
    block_type = [[HARD] * COLS for row in range(ROWS)]

    # Starting zone
    block_type[playerRow][playerCol] = PLAYER
    for i in range(playerCol + 1, transitionCol):
        block_type[playerRow][i] = SUPPORT
    block_type[playerRow][transitionCol] = LADDER
    for i in range(playerCol, transitionCol - 1, 2):
        block_type[assignmentRow][i] = SOFT
    block_type[assignmentRow][transitionCol] = LADDER

    # Ending zone
    block_type[ROWS - 2][transitionCol] = PRINCESS
    block_type[ROWS - 3][transitionCol] = SOFT  # Stop princess from walking

    # Send back partially-built level
    return block_type


def initSatisfiabilityClauses():
    global row_pointer

    for tuple in range(NUM_TUPLES):
        index = VARS_PER_TUPLE * tuple
        variable_states = [ABSENT] * NUM_VARS

        # Determine which variables were used in which clauses
        for offset in range(VARS_PER_TUPLE):
            var = array_form[index + offset]
            # Convert variable label --> variable state
            variable_states[abs(var) - 1] = sign(var)
        # Fill in gadget region for each variable for current tuple
        place_gadget(variable_states, row_pointer)
        row_pointer += GADGET_HEIGHT


# Map num to -1, 0, or 1 (Negated, Absent, Present)
def sign(num):
    return int(abs(num) / num)


def place_gadget(variable_states, bottom_row):
    startCol = 2  # Column of player's starting position
    transitionCol = COLS - 2  # Column with path (ladders) between areas

    # Create transition to next zone
    state[bottom_row][transitionCol] = LADDER
    state[bottom_row + 1][transitionCol] = SUPPORT
    # state[bottom_row + 2][transitionCol] is already HARD
    state[bottom_row + 3][transitionCol] = LADDER
    state[bottom_row + 4][transitionCol] = LADDER
    state[bottom_row + 5][transitionCol] = LADDER

    # Carve out walkable area
    for i in range(startCol, transitionCol, 2):
        state[bottom_row + 1][i] = SUPPORT
        state[bottom_row + 3][i] = SUPPORT
        state[bottom_row + 4][i] = SUPPORT

    # Place ladders according to gadget structure
    for varIndex in range(len(variable_states)):
        place_sub_gadget(
            variable_states[varIndex], bottom_row + 1, 2 * varIndex + 1)


# Clone sub-gadget ladder structure
def place_sub_gadget(varState, bottom_row, col):
    for i in range(SUB_GADGET_HEIGHT):
        state[bottom_row + i][col] = SUB_GADGETS[varState + 1][i]


# Change player's coordinate's and refresh the displayed game grid
def move(vector):
    global state, hidden, redRow, redCol, fresh
    vertical = 0
    horizontal = 1

    if vector == UP and state[redRow + 1][redCol] == SOFT:
        fresh = False

    else:
        state[redRow][redCol] = hidden
        redRow = redRow + vector[vertical]
        redCol = redCol + vector[horizontal]
        hidden = state[redRow][redCol]
        state[redRow][redCol] = PLAYER
        draw(min(redRow, redRow - vector[vertical]), max(redRow, redRow - vector[vertical]),
             min(redCol, redCol - vector[horizontal]), max(redCol, redCol - vector[horizontal]))


# Wrapper for move() that enables auto-solving
def force(vector):
    global state, hidden, redRow, redCol, fresh
    vertical = 0
    horizontal = 1

    target = state[redRow + vector[vertical]][redCol + vector[horizontal]]
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


def autoSolvePuzzle():
    global solution, solve, nested_form

    # compute vector sequence
    # find the solving variable assignment by brute force
    good_guess = []
    for guess in range(2 ** NUM_VARS):
        # Convert ordinal value of guess to its binary representation
        format_str = r'{:0' + str(NUM_VARS) + r'b}'
        parsed_guess = [int(format_str.format(guess)[j]) *
                        2 - 1 for j in range(NUM_VARS)]

        # Save current solution guess iff
        # Every clause has at least one variable that 'passes'
        # Meaning it yields a viable path through the clause
        if all([any([passes(nested_form[clause][var], parsed_guess)
                    for var in range(VARS_PER_TUPLE)]) for clause in range(NUM_TUPLES)]):
            good_guess = parsed_guess

    if len(good_guess) == 0:
        print("3SAT instance is not solvable!")
        solve = False
    else:
        # set variables
        for truthiness in good_guess:
            if truthiness == 1:
                solution.append(UP)
            solution.append(RIGHT)
            solution.append(RIGHT)
        # traverse level
        for tuple in range(NUM_TUPLES):
            solution.append(UP)
            solution.append(UP)
            solution.append(UP)
            lateral_blocks = 2 * (NUM_VARS + 1 - max([abs(nested_form[tuple][var])
                                                      for var in range(VARS_PER_TUPLE) if passes(nested_form[tuple][var], good_guess)]))

            # Move to nearest viable ladder
            for i in range(lateral_blocks):
                solution.append(LEFT)
            solution.append(UP)
            solution.append(UP)
            for i in range(lateral_blocks):
                solution.append(RIGHT)
            solution.append(UP)

        # Climb to princess
        solution.append(UP)
        solution.append(UP)
        solution.append(UP)


# Variable state (-1, 0, or 1) * variable truth setting (-1 or 1)
def passes(var, guess):
    return sign(var) * guess[abs(var) - 1] == 1


# Render the designated portion of the display
def draw(min_row, max_row, min_col, max_col):
    global state, screen
    rectangles = []

    for row in range(min_row, max_row + 1):
        # Create a rect for each block according to its saved state/color
        for col in range(min_col, max_col + 1):
            rectangles.append(pygame.draw.rect(screen, state[row][col],
                                               [col * BLOCK_DIM + 1, (ROWS - row - 1) * BLOCK_DIM + 1, BLOCK_DIM - 1, BLOCK_DIM - 1]))
    pygame.display.update(rectangles)  # Update the changed areas


# ----- Main program begins here -----
print()  # Give separation from pygame message

# Read in 3SAT problem
parser = argparse.ArgumentParser()
input_type = parser.add_mutually_exclusive_group()
input_type.add_argument('-i', metavar='VAR', dest='instance', nargs='*',
                        type=str, help="1 2 -3 is equivalent to the clause (x1 || x2 || !x3). Default is " + DEFAULT_3SAT)
input_type.add_argument('-f', dest='filename',
                        help="file containing an instance of 3SAT")
parser.add_argument('-s', dest='solver', action='store_true',
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

solve = args.solver

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

# Initialize drawing surface
screen = pygame.display.set_mode(window_size)

# set player position
hidden = SUPPORT

# Set up runtime constants
NUM_TUPLES = int(len(array_form) / 3)
NUM_VARS = max([abs(el) for el in array_form])
ROWS = 6 * (NUM_TUPLES + 1)
COLS = 3 + 2 * NUM_VARS
BLOCK_DIM = min(WINDOW_HEIGHT / ROWS, WINDOW_WIDTH / COLS)

# Set up variables
row_pointer = 3
done = False
fresh = True
solution = []
autosolve = 0
redRow = 1
redCol = 1
nested_form = [[array_form[VARS_PER_TUPLE * i + j]
                for j in range(VARS_PER_TUPLE)] for i in range(NUM_TUPLES)]

# Create bottom 3 rows & top 2 rows of puzzle
# Remaining area, including frame, is made of HARD blocks
state = initSpecialAreas()

# Place gadgets to construct puzzle
initSatisfiabilityClauses()

# Render initial gamestate on screen
draw(0, ROWS - 1, 0, COLS - 1)

if solve:
    autoSolvePuzzle()

# Main game loop
while not done:
    if solve:
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
    clock.tick(15)
    if hidden is PRINCESS:
        done = True
