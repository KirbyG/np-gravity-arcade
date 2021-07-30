#!/usr/bin/env python3

# this file reads user input, first from CLI, then in the game loop

# SETUP

import argparse
import pygame
from pygame.constants import K_ESCAPE
from puzzle import Puzzle
from popils import Popils
from megalit import Megalit
from artist import Artist
from common_constants import LEFT, RIGHT, DOWN, UP, ZERO, Vector

# default 3SAT instance. Will be ignored if user provides alternative
DEFAULT_3SAT = "examples/default.cnf"


# handle input from the command line
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='filename',
                        help="file containing an instance of 3SAT in DIMACS CNF format")
    parser.add_argument('-m', '--megalit', action='store_true',
                        help='reduce 3SAT to Megalit instead of Popils')
    parser.add_argument('-q', '--quick', action='store_true',
                        help='Increase game speed. Useful for playing back long autosolves')
    parser.add_argument('-s', '--solve', dest='solver', action='store_true',
                        help='run puzzle auto-solver')
    return parser.parse_args()


# add line break after pygame importing output
print()

# read in 3SAT problem
args = parse_arguments()

# set raw instance input data from command line or file
filepath = args.filename if args.filename else DEFAULT_3SAT

# create game instance of the correct type
puzzle = Puzzle(filepath)
game = Megalit(puzzle) if args.megalit else Popils(puzzle)
artist = Artist(game)

# set desired framerate
fps = 60 if args.quick else 15

# game loop
while not game.complete:
    # Capture player's attempt to quit manually
    try:
        event_list = pygame.event.get()
    except KeyboardInterrupt:
        # Exit upon SIGINT (Ctrl + C) in terminal
        game.complete = True

    # Normal user input mode
    for event in event_list:
        if event.type == pygame.QUIT:
            # Exit upon clicking X in corner of window
            game.complete = True
        elif event.type == pygame.KEYUP:
            if event.key == K_ESCAPE:
                # Exit upon hitting Esc
                game.complete = True
            # handle basic directional inputs
            elif event.key == pygame.K_LEFT:
                game.update(LEFT)
            elif event.key == pygame.K_RIGHT:
                game.update(RIGHT)
            elif event.key == pygame.K_UP:
                game.update(UP)
            elif event.key == pygame.K_DOWN:
                game.update(DOWN)
            elif event.key == pygame.K_SPACE:
                game.update(ZERO)

    # autosolver mode
    if args.solver and game.solution:
        game.update(game.solution[game.solution_step])
        game.solution_step += 1
        if game.solution_step == len(game.solution):
            game.complete = True

    # iterate game display with capped framerate
    artist.draw()
    artist.clock.tick(fps)
