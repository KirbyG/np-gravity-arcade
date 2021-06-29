# SETUP

import argparse
import pygame
from puzzle import Puzzle, DEFAULT_3SAT
from popils import Popils
from megalit import Megalit
from common_constants import LEFT, RIGHT, DOWN, UP, VARS_PER_CLAUSE, ZERO, Vector

# Measured in px
WINDOW_DIM = Vector(500, 1000)
MIN_BLOCK_DIM = 15

def parse_arguments():
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


# make initialization calls to the graphics library pygame
def init_pygame(window_title):
    # Initialize pygame submodules
    pygame.init()
    # Set window title
    pygame.display.set_caption(window_title)
    # Initialize drawing surface
    screen = pygame.display.set_mode(WINDOW_DIM())

    clock = pygame.time.Clock()

    return screen, clock

# DRAWING

'''def set_tile_size(self):
    # Scale size of game blocks (within reasonable limits)
    block_height = max(WINDOW_HEIGHT / self.num_rows, MIN_BLOCK_DIM)
    block_width = max(WINDOW_WIDTH / self.num_cols, MIN_BLOCK_DIM)

    # Blocks are square, so just use smaller side length
    return min(block_height, block_width)'''

# graphical helper function: return a rectangle where the specified block in the grid should be drawn
def grid_to_px(x, y):
    # Side length of game blocks (which are all squares)
    block_dim = min((WINDOW_DIM / game.grid.dim)())

    return [x * block_dim + 1, (game.grid.dim.y - y - 1) * block_dim + 1, block_dim - 1, block_dim - 1]


# Render the designated portion of the display
def draw(screen, game):
    for x in range(game.grid.dim.x):
        for y in range(game.grid.dim.y):
            pygame.draw.rect(
                screen, game.grid[x, y].color, grid_to_px(x, y))

    # draw player
    pygame.draw.rect(screen, game.player.color,
                      grid_to_px(game.player.pos.x, game.player.pos.y))

    pygame.display.update()  # update the changed areas



# ----- Main program code begins here -----
print()  # Give separation from pygame message

# Read in 3SAT problem
args = parse_arguments()

# set raw instance input data from command line or file
if args.filename:
    with open(args.filename) as file:
        raw_input = file.readline()
elif args.instance:
    raw_input = " ".join(args.instance)
else:
    raw_input = DEFAULT_3SAT

# create game instance of the correct type
puzzle = Puzzle(raw_input)
game = Megalit(puzzle) if args.megalit else Popils(puzzle)

# create render surface and game clock, set window title
screen, clock = init_pygame(
    'Megalit Reduction' if args.megalit else 'Popils Reduction')

# render initial gamestate
draw(screen, game)

# game loop
while not game.complete:
    # update gamestate
    if args.solver:  # autosolver mode
        game.update(game.solution[game.solution_step])
        game.solution_step += 1
        if game.solution_step == len(game.solution):
            game.complete = True
    else:  # user input mode
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.complete = True
            elif event.type == pygame.KEYUP:  # pass basic directional inputs to game
                if event.key == pygame.K_LEFT:
                    game.update(LEFT)
                elif event.key == pygame.K_RIGHT:
                    game.update(RIGHT)
                elif event.key == pygame.K_UP:
                    game.update(UP)
                elif event.key == pygame.K_DOWN:
                    game.update(DOWN)
                elif event.key == pygame.K_SPACE:
                    game.update(ZERO)
    # iterate game display with framerate capped at 15 FPS
    draw(screen, game)
    clock.tick(15)
