from game import Game
from common import LEFT, DOWN, UP, RIGHT
from common import X, Y
from common import LADDER, SUPPORT, HARD, BREAKABLE, PRINCESS
from common import _
import numpy as np

# popils-specific gadgets
VAR_NEGATED = [LADDER, LADDER, SUPPORT, LADDER]
VAR_ABSENT = [LADDER, SUPPORT, LADDER, SUPPORT]
VAR_PRESENT = [SUPPORT, LADDER, LADDER, SUPPORT]
VAR_GADGETS = [VAR_NEGATED, VAR_ABSENT, VAR_PRESENT]

# popils-specific gadget sizes
SUB_GADGET_HEIGHT = 4
GADGET_HEIGHT = 6


class Popils(Game):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.player = np.array([1, 1])
        super().__init__(puzzle)

################################################################################
    # REDUCE and its helpers build a popils level expressing the given 3SAT
    # puzzle
    def reduce(self):
        # Set dimensions of grid and initialize
        self.grid = np.full(
            (
                3 + (2 * self.puzzle.num_vars),
                6 * (self.puzzle.num_clauses + 1)
            ),
            HARD
        )

        ### Build static level features
        # bottom of the level: starting zone used for setting variables
        self.grid[np.arange(1, self.grid.shape[X] - 2), 1] = SUPPORT #walkway
        self.grid[self.grid.shape[X] - 2, [1, 2]] = LADDER #ascend to first clause
        self.grid[np.arange(1, self.grid.shape[X] - 3, 2), 2] = BREAKABLE #var setters

        # win condition / princess holding cell
        self.grid[self.grid.shape[X] - 2, self.grid.shape[Y] - 2] = PRINCESS
        self.grid[self.grid.shape[X] - 2, self.grid.shape[Y] - 3] = BREAKABLE

        ### Place gadgets to construct puzzle
        bottom = 3
        for clause in range(self.puzzle.num_clauses):
            self.construct_clause(self.puzzle.expanded_form[clause], bottom)
            bottom += GADGET_HEIGHT

    # REDUCE HELPER: 
    def construct_clause(self, var_settings, bottom):
        # Create transition to next zone
        self.grid[self.grid.shape[X] - 2, bottom] = LADDER
        self.grid[self.grid.shape[X] - 2, bottom + 1] = SUPPORT
        # bottom + 2 is already correctly set to 'hard'
        self.grid[self.grid.shape[X] - 2, np.arange(bottom + 3, bottom + 6)] = LADDER

        # Carve out walkable area, skipping gadget columns
        self.grid[np.ix_(
            np.arange(2, self.grid.shape[X] - 2, 2),
            np.array([1, 3, 4]) + bottom
        )] = SUPPORT

        # Place columns of ladders and support blocks representing variable encoding in
        # this clause
        for var_index in range(len(var_settings)):
            var_state = var_settings[var_index]
            self.grid[
                2 * var_index + 1, #every other column
                bottom + 1 + np.arange(SUB_GADGET_HEIGHT)
            ] = VAR_GADGETS[var_state + 1]

########################################################################################
    # SOLVE computes the popils-specific solving move sequence for the given 3SAT puzzle
    def solve(self):
        sol = np.empty((0,2), dtype='int')
        if self.puzzle.solution:
            # make variable assignments
            for truthiness in self.puzzle.solution:
                if truthiness == 1:
                    sol = np.vstack([sol, UP])
                sol = np.vstack([sol, np.tile(RIGHT, (2,1))])

            # traverse level
            for clause in range(self.puzzle.num_clauses):
                # climb ladder to enter clause
                sol = np.vstack([sol, np.tile(UP, (3,1))])

                # find nearest viable ladder
                satisfied = self.puzzle.satisfied_vars(
                    self.puzzle.three_sat[clause], self.puzzle.solution)
                closest = max([abs(var) for var in satisfied])
                lateral_blocks = 2 * (self.puzzle.num_vars + 1 - closest)

                # move to nearest viable ladder
                sol = np.vstack([sol, np.tile(LEFT, (lateral_blocks,1))])

                # climb to next clause
                sol = np.vstack([sol, np.tile(UP, (2,1))])

                # go back to the main ladder
                sol = np.vstack([sol, np.tile(RIGHT, (lateral_blocks,1))])

                # get in position to traverse the next clause
                sol = np.vstack([sol, UP])

            # climb to princess!
            sol = np.vstack([sol, np.tile(UP, (3,1))])
        else:
            print("INFO | Not running Popils solver because 3SAT was not solved.")
        return sol

    # SOLVE HELPER
    def update(self, movement):
        print(self.player)
        print(movement)
        print(self.player+movement)
        target = self.grid[_(self.player + movement)]

        if all(movement == UP):
            if target == BREAKABLE:
                airspace = np.arange(self.player[Y] + 1, self.grid.shape[Y])
                np.put(
                    self.grid[self.player[X],:],#along the y-axis
                    airspace,#to top
                    self.grid[self.player[X],airspace[1]:airspace[-1]+1]
                )
            elif self.grid[_(self.player)] == LADDER and (target != HARD):
                self.move(UP)
        elif target != HARD:
            self.move(movement)
            while (
                self.grid[_(self.player + DOWN)] == SUPPORT and
                self.grid[_(self.player)] == SUPPORT
            ):
                self.move(DOWN)

    # SOLVE HELPER
    def move(self, vector):
        self.player += vector

        if self.grid[_(self.player)] == PRINCESS:
            self.complete = True
