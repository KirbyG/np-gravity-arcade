import argparse
import pygame

# Default 3SAT instance. Will be ignored if user provides alternative
DEFAULT_3SAT = '1 2 3 -2 -3 4 1 -3 6 -1 4 5 2 -4 -6'

# Definition of 3SAT
VARS_PER_CLAUSE = 3


def parseArguments():
    parser = argparse.ArgumentParser()
    input_type = parser.add_mutually_exclusive_group()
    input_type.add_argument('-i', metavar='VAR', dest='instance', nargs='*',
                            type=str, help="1 2 -3 is equivalent to the clause (x1 || x2 || !x3). Default is " + DEFAULT_3SAT)
    input_type.add_argument('-f', dest='filename',
                            help="file containing an instance of 3SAT")
    parser.add_argument('-s', dest='solver', action='store_true',
                        help='run puzzle auto-solver')
    return parser.parse_args()


def convertToCanonicalForm(args):
    # Read in problem from stdin or file
    if args.instance:
        raw_input = " ".join(args.instance)
    elif args.filename:
        with open(args.filename) as file:
            raw_input = file.readline()
    else:
        raw_input = DEFAULT_3SAT

    # Attempt to convert input to a list of integers
    try:
        array_form = [int(el) for el in str.split(raw_input)]
    except:
        print("WARNING: Malformed input. Default 3SAT instance has been used instead.")
        array_form = [int(el) for el in str.split(DEFAULT_3SAT)]

    # Truncate input if there are variables that don't form a full clause
    extra_inputs = len(array_form) % 3
    array_form = array_form[:-extra_inputs]
    if extra_inputs != 0:
        print("WARNING: 3SAT requires tuples of exactly size 3. Input has been truncated appropriately.")

    NUM_TUPLES = int(len(array_form) / 3)

    # 2D representation of 3SAT problem (clauses contain vars)
    nested_form = [[array_form[VARS_PER_CLAUSE * i + j]
                    for j in range(VARS_PER_CLAUSE)] for i in range(NUM_TUPLES)]
    reduced_form = convertToReducedForm(raw_input, nested_form)
    return reduced_form


def convertToReducedForm(raw_input, nested_form):
    # Relabel variables to smallest possible numbers
    var_set = {abs(var) for var in raw_input}
    num_unique_vars = len(var_set)
    for index in range(num_unique_vars):
        if not index in var_set:
            to_relabel = min([elem for elem in var_set if elem <= index])
            var_set.discard(to_relabel)
            var_set.add(index)
            nested_form = [[index if var == to_relabel else var for var in clause]
                           for clause in nested_form]

    # Remove malformed clauses with duplicate vars
    nested_form = [clause for clause in nested_form if len(
        {abs(var) for var in clause}) == VARS_PER_CLAUSE]

    return nested_form


def printThreeSat(three_sat):
    print("CNF form of 3SAT: " + " ^ ".join(
        ["(" + " V ".join(clause) + ")" for clause in three_sat]))


print()  # Give separation from pygame message

# Read in 3SAT problem
args = parseArguments()

# Put 3SAT instance into standard format
canonical_form = convertToCanonicalForm(args)

# Print pretty version of 3SAT in conjunctive normal form
printThreeSat(canonical_form)

# Initialize pygame submodules
pygame.init()
clock = pygame.time.Clock()

# Set window title
pygame.display.set_caption('Test')

# Initialize drawing surface
window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
screen = pygame.display.set_mode(window_size)

# Set up runtime constants

NUM_VARS = max([abs(el) for el in array_form])
ROWS = 6 * (NUM_TUPLES + 1)
COLS = 3 + 2 * NUM_VARS
BLOCK_DIM = min(WINDOW_HEIGHT / ROWS, WINDOW_WIDTH / COLS)

# Set up variables
done = False

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
