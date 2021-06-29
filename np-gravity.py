# this file reads user input

# SETUP

import argparse
import pygame
from puzzle import Puzzle, DEFAULT_3SAT
from popils import Popils
from megalit import Megalit
from artist import Artist
from common_constants import LEFT, RIGHT, DOWN, UP, ZERO, Vector

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
game = Megalit(puzzle) if not args.megalit else Popils(puzzle)
artist = Artist(game)

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
    artist.draw()
    artist.clock.tick(15)
