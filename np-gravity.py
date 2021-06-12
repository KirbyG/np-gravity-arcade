import argparse
import pygame
from puzzle import Puzzle
from popils import Popils
from megalit import Megalit
from common_constants import LEFT, RIGHT, DOWN, UP, VARS_PER_CLAUSE
from game import DEFAULT_3SAT

# Measured in px
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 1000

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
    window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
    screen = pygame.display.set_mode(window_size)

    clock = pygame.time.Clock()

    return screen, clock

# graphical helper function: return a rectangle where the specified block in the grid should be drawn
def grid_to_px(row, col):
     # Side length of game blocks (which are all squares)
    block_dim = min(WINDOW_HEIGHT / game.num_rows,
                    WINDOW_WIDTH / game.num_cols)

    return [col * block_dim + 1, (game.num_rows - row - 1) * block_dim + 1, block_dim - 1, block_dim - 1]

# Render the designated portion of the display
def draw(screen, game):
    rectangles = []

    # draw blocks from the game grid if they are in the updated zone
    for row in range(game.altered_rows):
        for col in range(game.altered_cols):
            rectangles.append(pygame.draw.rect(
                screen, game.grid[row][col].color, grid_to_px(row, col)))
    
    # draw player
    rectangles.append(pygame.draw.rect(screen, game.player.color, grid_to_px(game.player.row, game.player.col)))

    pygame.display.update(rectangles)  # update the changed areas
    game.altered_rows = game.altered_cols = [0, 0] # reset bounds to indicate drawing is complete


# ----- Main program code begins here -----
print()  # Give separation from pygame message

# Read in 3SAT problem
args = parse_arguments()

# set raw instance input data from command line or file
if args.filename:
    with open(args.filename) as file:
        raw_input = file.readline()
else:
    raw_input = args.instance

# create game instance of the correct type
game = Megalit(Puzzle(raw_input)) if args.megalit else Popils(Puzzle(raw_input))

# create render surface and game clock, set window title
screen, clock = init_pygame('Megalit Reduction' if args.megalit else 'Popils Reduction')

# initial gamestate render
draw(screen, game)

# game loop
while not game.complete:
    # update gamestate
    if len(game.solution) != 0: # autosolver mode
        game.update(game.solution[game.solution_step])
        game.solution_step += 1
    else: # user input mode
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.complete = True
            elif event.type == pygame.KEYUP: # pass basic directional inputs to game
                if event.key == pygame.K_LEFT:
                    game.update(LEFT)
                elif event.key == pygame.K_RIGHT:
                    game.update(RIGHT)
                elif event.key == pygame.K_UP:
                    game.update(UP)
                elif event.key == pygame.K_DOWN:
                    game.update(DOWN)
    # iterate game display with framerate capped at 15 FPS
    draw(screen, game)
    clock.tick(15)
