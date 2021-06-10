import pygame
import argparse

from popils_constants import *


# ----- Function definitions -----
def initSpecialAreas():
    player_row = player_col = 1
    assignment_row = 2
    transition_col = COLS - 2  # Column with path (ladders) between areas
    # Initially set entire zone to indestructible blocks
    # Using this "*" notation twice doesn't produce expected results
    #   because Python just makes pointers to original tuple
    block_type = [[HARD] * COLS for row in range(ROWS)]

    # Starting zone
    block_type[player_row][player_col] = PLAYER
    for i in range(player_col + 1, transition_col):
        block_type[player_row][i] = SUPPORT
    block_type[player_row][transition_col] = LADDER
    for i in range(player_col, transition_col - 1, 2):
        block_type[assignment_row][i] = SOFT
    block_type[assignment_row][transition_col] = LADDER

    # Ending zone
    block_type[ROWS - 2][transition_col] = PRINCESS
    block_type[ROWS - 3][transition_col] = SOFT  # Stop princess from walking

    # Send back partially-built level
    return block_type


def initSatisfiabilityClauses():
    row_pointer = 3

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
    start_col = 2
    transition_col = COLS - 2  # Column with path (ladders) between areas

    # Create transition to next zone
    state[bottom_row][transition_col] = LADDER
    state[bottom_row + 1][transition_col] = SUPPORT
    # state[bottom_row + 2][transition_col] is already HARD
    state[bottom_row + 3][transition_col] = LADDER
    state[bottom_row + 4][transition_col] = LADDER
    state[bottom_row + 5][transition_col] = LADDER

    # Carve out walkable area, skipping gadget columns
    for i in range(start_col, transition_col, 2):
        state[bottom_row + 1][i] = SUPPORT
        state[bottom_row + 3][i] = SUPPORT
        state[bottom_row + 4][i] = SUPPORT

    # Place ladders according to gadget structure
    for var_index in range(len(variable_states)):
        place_sub_gadget(
            variable_states[var_index], bottom_row + 1, 2 * var_index + 1)


# Clone sub-gadget ladder structure
def place_sub_gadget(var_state, bottom_row, col):
    for i in range(SUB_GADGET_HEIGHT):
        state[bottom_row + i][col] = SUB_GADGETS[var_state + 1][i]


# Change player's coordinates and refresh the displayed game grid
def move(vector, player):
    vertical = 0
    horizontal = 1

    state[player.row][player.col] = player.occupying
    player.row += vector[vertical]
    player.col += vector[horizontal]
    player.occupying = state[player.row][player.col]
    state[player.row][player.col] = PLAYER
    draw(min(player.row, player.row - vector[vertical]), max(player.row, player.row - vector[vertical]),
         min(player.col, player.col - vector[horizontal]), max(player.col, player.col - vector[horizontal]))


# Wrapper for move() that enables auto-solving
def force(vector, player):
    global state
    vertical = 0
    horizontal = 1
    target = state[player.row + vector[vertical]
                   ][player.col + vector[horizontal]]

    if vector == UP:
        if target == SOFT:
            for falling_row in range(player.row + 1, ROWS - 1):
                state[falling_row][player.col] = state[falling_row + 1][player.col]
            state[ROWS - 1][player.col] = HARD
            draw(player.row + 1, ROWS - 1, player.row, player.col)
        elif player.occupying == LADDER and (target != HARD):
            move(UP, player)
    elif target != HARD:
        move(vector, player)


def generateSolution():
    global nested_form
    steps = []

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
        return []
    else:
        # set variables
        for truthiness in good_guess:
            if truthiness == 1:
                steps.append(UP)
            steps.append(RIGHT)
            steps.append(RIGHT)
        # traverse level
        for tuple in range(NUM_TUPLES):
            steps.append(UP)
            steps.append(UP)
            steps.append(UP)
            lateral_blocks = 2 * (NUM_VARS + 1 - max([abs(nested_form[tuple][var])
                                                      for var in range(VARS_PER_TUPLE) if passes(nested_form[tuple][var], good_guess)]))

            # Move to nearest viable ladder
            for i in range(lateral_blocks):
                steps.append(LEFT)
            steps.append(UP)
            steps.append(UP)
            for i in range(lateral_blocks):
                steps.append(RIGHT)
            steps.append(UP)

        # Climb to princess
        steps.append(UP)
        steps.append(UP)
        steps.append(UP)

        return steps


# Returns the product of variable state (-1, 0, or 1) and variable truth setting (-1 or 1)
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

array_form = [int(el) for el in str.split(three_sat)]
truncation_needed = False
while len(array_form) % 3 != 0:
    array_form = array_form[:-1]
    truncation_needed = True
if truncation_needed:
    print("WARNING: 3SAT requires tuples of exactly size 3. Input has been truncated appropriately.")
print("3SAT instance: " + str(array_form))
# TODO print pretty version of 3SAT in conjunctive normal form

# Initialize pygame submodules
pygame.init()
clock = pygame.time.Clock()

# Set window title
pygame.display.set_caption('Test')

# Initialize drawing surface
window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
screen = pygame.display.set_mode(window_size)

# Set up runtime constants
NUM_TUPLES = int(len(array_form) / 3)
NUM_VARS = max([abs(el) for el in array_form])
ROWS = 6 * (NUM_TUPLES + 1)
COLS = 3 + 2 * NUM_VARS
BLOCK_DIM = min(WINDOW_HEIGHT / ROWS, WINDOW_WIDTH / COLS)

# Set up variables
done = False
nested_form = [[array_form[VARS_PER_TUPLE * i + j]
                for j in range(VARS_PER_TUPLE)] for i in range(NUM_TUPLES)]
solution = []
if args.solver:
    solution = generateSolution()
    solution_step = 0

# Create bottom 3 rows & top 2 rows of puzzle
# Remaining area, including frame, is made of HARD blocks
state = initSpecialAreas()

# Initialize player position
player = Player()

# Place gadgets to construct puzzle
initSatisfiabilityClauses()

# Render initial gamestate on screen
draw(0, ROWS - 1, 0, COLS - 1)

# Main game loop
while not done:
    if len(solution) != 0:
        force(solution[solution_step], player)
        solution_step += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        else:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    force(LEFT, player)
                elif event.key == pygame.K_RIGHT:
                    force(RIGHT, player)
                elif event.key == pygame.K_UP:
                    force(UP, player)
                elif event.key == pygame.K_DOWN and state[player.row - 1][player.col] != HARD:
                    force(DOWN, player)
        # If player walks off the top of a ladder, make them fall
        while (state[player.row - 1][player.col] == SUPPORT and player.occupying == SUPPORT):
            force(DOWN, player)
    clock.tick(15)  # Cap framerate at 15 FPS
    if player.occupying is PRINCESS:
        done = True
pygame.quit()