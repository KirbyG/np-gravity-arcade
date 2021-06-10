import pygame
import argparse




# ----- Function definitions -----



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
    steps = []
    global nested_form
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