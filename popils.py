from game import Game, Player, Block
from common import LEFT, DOWN, UP, RIGHT
from common import X, Y
from common import LADDER, SUPPORT, HARD, BREAKABLE, PRINCESS
import numpy as np

# popils-specific gadgets
SUB_GADGET_NEGATED = [LADDER, LADDER, SUPPORT, LADDER]
SUB_GADGET_ABSENT = [LADDER, SUPPORT, LADDER, SUPPORT]
SUB_GADGET_PRESENT = [SUPPORT, LADDER, LADDER, SUPPORT]
SUB_GADGETS = [SUB_GADGET_NEGATED, SUB_GADGET_ABSENT, SUB_GADGET_PRESENT]

# popils-specific gadget sizes
SUB_GADGET_HEIGHT = 4
GADGET_HEIGHT = 6


class Popils(Game):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.player = Player(np.array([1, 1]))
        super().__init__(puzzle)

    def reduce(self):
        # set dimensions of grid and initialize
        self.grid = np.full(
            (
                3 + (2 * self.puzzle.num_vars),
                6 * (self.puzzle.num_clauses + 1)
            ),
            HARD
        )

        # build static level features
        self.build_frame()

        # Place gadgets to construct puzzle
        self.build_clauses()

    # reduce helper function: create static areas of the grid that depend only on instance size
    def build_frame(self):
        # Starting zone
        for x in range(self.player.pos[X], self.grid.shape.X - 2):
            self.grid[x, self.player.pos[Y]] = SUPPORT
        

        self.grid[self.grid.shape.X - 2, self.player.pos[Y]].type = LADDER

        for x in range(self.player.pos[X], self.grid.shape.X - 3, 2):
            self.grid[x, 2].type = BREAKABLE

        self.grid[self.grid.shape.x - 2, 2].type = LADDER

        # Ending zone
        self.grid[self.grid.shape.X - 2, self.grid.shape.Y - 2].type = PRINCESS

        # Stop princess from walking
        self.grid[self.grid.shape.X - 2, self.grid.shape.Y - 3].type = BREAKABLE

    # reduce helper function

    def build_clauses(self):
        bottom_y = 3

        for clause in range(self.puzzle.num_clauses):
            # Fill in gadget region for each variable for current tuple
            self.place_gadget(self.puzzle.expanded_form[clause], bottom_y)
            bottom_y += GADGET_HEIGHT

    # reduce helper function
    def place_gadget(self, variable_states, bottom_y):
        # Create transition to next zone
        self.grid[self.grid.shape.X - 2, bottom_y].type = LADDER
        self.grid[self.grid.shape.X - 2, bottom_y + 1].type = SUPPORT

        # bottom_y + 2 is already correctly set to 'hard'
        self.grid[self.grid.shape.X - 2, bottom_y + 3].type = LADDER
        self.grid[self.grid.shape.X - 2, bottom_y + 4].type = LADDER
        self.grid[self.grid.shape.X - 2, bottom_y + 5].type = LADDER

        # Carve out walkable area, skipping gadget columns
        for x in range(2, self.grid.dim.x - 2, 2):
            self.grid[x, bottom_y + 1].type = SUPPORT
            self.grid[x, bottom_y + 3].type = SUPPORT
            self.grid[x, bottom_y + 4].type = SUPPORT

        # Place 'ladder's according to gadget structure
        for var_index in range(len(variable_states)):
            self.place_sub_gadget(
                variable_states[var_index], bottom_y + 1, 2 * var_index + 1)

    # reduce helper function: place a part of a gadget corresponding to the state of 1 variable
    def place_sub_gadget(self, var_state, bottom_y, x):
        for delta_y in range(SUB_GADGET_HEIGHT):
            self.grid[x, bottom_y +
                      delta_y].type = SUB_GADGETS[var_state + 1][delta_y]

    # compute the popils-specific solving move sequence for the given 3SAT instance
    def solve(self):
        sol = np.empty(0)
        if self.puzzle.solution:
            # make variable assignments
            for truthiness in self.puzzle.solution:
                if truthiness == 1:
                    sol = np.append(sol, UP)
                sol = np.concatenate([sol, np.tile(RIGHT, 2)])

            # traverse level
            for clause in range(self.puzzle.num_clauses):
                # climb ladder to enter clause
                sol = np.concatenate([sol, np.tile(UP, 3)])

                # find nearest viable ladder
                satisfied = self.puzzle.satisfied_vars(
                    self.puzzle.three_sat[clause], self.puzzle.solution)
                closest = max([abs(var) for var in satisfied])
                lateral_blocks = 2 * (self.puzzle.num_vars + 1 - closest)

                # move to nearest viable ladder
                sol = np.concatenate([sol, np.tile(LEFT, lateral_blocks)])

                # climb to next clause
                sol = np.concatenate([sol, np.tile(UP, 2)])

                # go back to the main ladder
                sol = np.concatenate([sol, np.tile(RIGHT, lateral_blocks)])

                # get in position to traverse the next clause
                sol = np.append(sol, UP)

            # climb to princess!
            sol = np.concatenate([sol, np.tile(UP, 3)])
        else:
            print("INFO | Not running Popils solver because 3SAT was not solved.")
        return sol

    # vector is one of the common vectors imported from common
    def update(self, vector):
        target = self.grid[self.player.pos + vector]

        if vector == UP:
            if target.type == BREAKABLE:
                for falling_y in range(self.player.pos[Y] + 1, self.grid.shape.Y - 1):
                    self.grid[self.player.pos[X],
                              falling_y] = self.grid[self.player.pos[X], falling_y + 1]
            elif self.grid[self.player.pos].type == LADDER and (target.type != HARD):
                self.move(UP)
        elif target.type != HARD:
            self.move(vector)
            while (self.grid[self.player.pos + DOWN].type == SUPPORT and self.grid[self.player.pos].type == SUPPORT):
                self.move(DOWN)

    # update helper
    def move(self, vector):
        self.player.pos += vector

        if self.grid[self.player.pos].type == PRINCESS:
            self.complete = True
