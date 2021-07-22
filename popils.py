from game import Game, Player, Block
from common_constants import LEFT, DOWN, UP, RIGHT, ZERO, VARS_PER_CLAUSE, COLORS, Vector, Grid


# popils-specific gadgets
SUB_GADGET_NEGATED = ['ladder', 'ladder', 'support', 'ladder']
SUB_GADGET_ABSENT = ['ladder', 'support', 'ladder', 'support']
SUB_GADGET_PRESENT = ['support', 'ladder', 'ladder', 'support']
SUB_GADGETS = [SUB_GADGET_NEGATED, SUB_GADGET_ABSENT, SUB_GADGET_PRESENT]

# popils-specific gadget sizes
SUB_GADGET_HEIGHT = 4
GADGET_HEIGHT = 6


class Popils(Game):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.player = Player(Vector(1, 1))
        super().__init__(puzzle)

    def reduce(self):
        # set dimensions of grid and initialize
        x_dim = 3 + (2 * self.puzzle.num_vars)
        y_dim = 6 * (self.puzzle.num_clauses + 1)
        self.grid = Grid(x_dim, y_dim, lambda: Block('hard'))

        # build static level features
        self.build_frame()

        # Place gadgets to construct puzzle
        self.build_clauses()

    # reduce helper function: create static areas of the grid that depend only on instance size
    def build_frame(self):
        # Starting zone
        for x in range(self.player.pos.x, self.grid.dim.x - 2):
            self.grid[x, self.player.pos.y].type = 'support'

        self.grid[self.grid.dim.x - 2, self.player.pos.y].type = 'ladder'

        for x in range(self.player.pos.x, self.grid.dim.x - 3, 2):
            self.grid[x, 2].type = 'breakable'

        self.grid[self.grid.dim.x - 2, 2].type = 'ladder'

        # Ending zone
        self.grid[self.grid.dim.x - 2, self.grid.dim.y - 2].type = 'princess'

        # Stop princess from walking
        self.grid[self.grid.dim.x - 2, self.grid.dim.y - 3].type = 'breakable'

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
        self.grid[self.grid.dim.x - 2, bottom_y].type = 'ladder'
        self.grid[self.grid.dim.x - 2, bottom_y + 1].type = 'support'

        # bottom_y + 2 is already correctly set to 'hard'
        self.grid[self.grid.dim.x - 2, bottom_y + 3].type = 'ladder'
        self.grid[self.grid.dim.x - 2, bottom_y + 4].type = 'ladder'
        self.grid[self.grid.dim.x - 2, bottom_y + 5].type = 'ladder'

        # Carve out walkable area, skipping gadget columns
        for x in range(2, self.grid.dim.x - 2, 2):
            self.grid[x, bottom_y + 1].type = 'support'
            self.grid[x, bottom_y + 3].type = 'support'
            self.grid[x, bottom_y + 4].type = 'support'

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
        self.solution = []
        if self.puzzle.solution:
            # make variable assignments
            for truthiness in self.puzzle.solution:
                if truthiness == 1:
                    self.solution.append(UP)
                self.solution.append(RIGHT)
                self.solution.append(RIGHT)

            # traverse level
            for clause in range(self.puzzle.num_clauses):
                # climb ladder to enter clause
                self.solution.append(UP)
                self.solution.append(UP)
                self.solution.append(UP)

                # find nearest viable ladder
                satisfied = self.puzzle.satisfied_vars(
                    self.puzzle.three_sat[clause], self.puzzle.solution)
                closest = max([abs(var) for var in satisfied])
                lateral_blocks = 2 * (self.puzzle.num_vars + 1 - closest)

                # move to nearest viable ladder
                for i in range(lateral_blocks):
                    self.solution.append(LEFT)

                # climb to next clause
                self.solution.append(UP)
                self.solution.append(UP)

                # go back to the main ladder
                for i in range(lateral_blocks):
                    self.solution.append(RIGHT)

                # get in position to traverse the next clause
                self.solution.append(UP)

            # climb to princess!
            self.solution.append(UP)
            self.solution.append(UP)
            self.solution.append(UP)
        else:
            print("WARNING | Not running Popils solver because 3SAT could not be solved.")

    # vector is one of the common vectors imported from common_constants
    def update(self, vector):
        target = self.grid[self.player.pos + vector]

        if vector == UP:
            if target.type == 'breakable':
                for falling_y in range(self.player.pos.y + 1, self.grid.dim.y - 1):
                    self.grid[self.player.pos.x,
                              falling_y] = self.grid[self.player.pos.x, falling_y + 1]
            elif self.grid[self.player.pos].type == 'ladder' and (target.type != 'hard'):
                self.move(UP)
        elif target.type != 'hard':
            self.move(vector)
            while (self.grid[self.player.pos + DOWN].type == 'support' and self.grid[self.player.pos].type == 'support'):
                self.move(DOWN)

    # update helper
    def move(self, vector):
        self.player.pos += vector

        if self.grid[self.player.pos].type == 'princess':
            self.complete = True
