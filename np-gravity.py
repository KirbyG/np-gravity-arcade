import argparse
import pygame
from puzzle import Puzzle
from popils import Popils
from megalit import Megalit
from popils_constants import Player
import common_constants as const

# Default 3SAT instance. Will be ignored if user provides alternative
DEFAULT_3SAT = '1 2 3 -2 -3 4 1 -3 6 -1 4 5 2 -4 -6'

# Definition of 3SAT
VARS_PER_CLAUSE = 3

# Measured in px
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 1000


def parseArguments():
    parser = argparse.ArgumentParser()
    input_type = parser.add_mutually_exclusive_group()
    input_type.add_argument('-i', metavar='VAR', dest='instance', nargs='*',
                            type=str, help="1 2 -3 is equivalent to the clause (x1 || x2 || !x3). Default is " + DEFAULT_3SAT)
    input_type.add_argument('-f', dest='filename',
                            help="file containing an instance of 3SAT")
    parser.add_argument('-s', dest='solver', action='store_true',
                        help='run puzzle auto-solver')
    parser.add_argument('-m', '--megalit', action='store_true',
                        help='reduce 3SAT to Megalit instead of Popils')
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


def setUpPygame():
    # Initialize pygame submodules
    pygame.init()
    # Set window title
    pygame.display.set_caption('NP-Gravity')
    # Initialize drawing surface
    window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
    screen = pygame.display.set_mode(window_size)

    clock = pygame.time.Clock()

    return screen, clock


# Render the designated portion of the display
def draw(bounds, screen, game, player):
    rectangles = []
    min_row = bounds[0]
    max_row = bounds[1]
    min_col = bounds[2]
    max_col = bounds[3]

    # Side length of game blocks (which are all squares)
    block_dim = min(WINDOW_HEIGHT / game.num_rows,
                    WINDOW_WIDTH / game.num_cols)

    for row in range(min_row, max_row + 1):
        # Create a rect for each block according to its saved state/color
        for col in range(min_col, max_col + 1):
            rect_corners = [
                col * block_dim + 1, (game.num_rows - row - 1) * block_dim + 1, block_dim - 1, block_dim - 1]
            rectangles.append(pygame.draw.rect(
                screen, game.state[row][col].color, rect_corners))
    player_loc = [
        player.col * block_dim + 1, (game.num_rows - player.row - 1) * block_dim + 1, block_dim - 1, block_dim - 1]
    rectangles.append(pygame.draw.rect(screen, player.color, player_loc))
    pygame.display.update(rectangles)  # Update the changed areas


# Only run this code if this file is executed directly (not imported)
if __name__ == "__main__":
    print()  # Give separation from pygame message

    # Read in 3SAT problem
    args = parseArguments()

    # Put 3SAT instance into standard format
    canonical_form = convertToCanonicalForm(args)

    # Print pretty version of 3SAT in conjunctive normal form
    printThreeSat(canonical_form)

    # Create render surface and synchronization clock
    screen, clock = setUpPygame()

    # Solve the given 3SAT instance
    puzzle = Puzzle(canonical_form)

    # Instantiate game representation
    if args.megalit:
        game = Megalit(puzzle)
    else:
        game = Popils(puzzle)

    # Initialize player position
    player = Player()

    # Render initial gamestate on screen
    window_boundaries = [0, game.game.num_rows - 1, 0, game.game.num_cols - 1]
    draw(window_boundaries, screen, game, player)

    # Main game loop
    while not game.complete:
        altered_region = [0, 0, 0, 0]
        if len(game.solution) != 0:
            game.force(game.solution[game.solution_step], player)
            game.solution_step += 1
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.complete = True
                else:
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            altered_region = game.force(const.LEFT, player)
                        elif event.key == pygame.K_RIGHT:
                            altered_region = game.force(const.RIGHT, player)
                        elif event.key == pygame.K_UP:
                            altered_region = game.force(const.UP, player)
                        elif event.key == pygame.K_DOWN:
                            altered_region = game.force(const.DOWN, player)
        draw(altered_region, screen, game, player)
        # Cap framerate at 15 FPS
        clock.tick(15)
