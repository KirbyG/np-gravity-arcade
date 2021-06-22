from game import Game, Player, Block
from common_constants import LEFT, DOWN, UP, RIGHT, ZERO, VARS_PER_CLAUSE, COLORS



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
        self.player = Player([1, 1])
        super().__init__(puzzle)
        self.altered_rows = [0, self.num_rows - 1]
        self.altered_cols = [0, self.num_cols - 1]

    def reduce(self, puzzle):
        # set dimensions of grid
        self.num_rows = 6 * (puzzle.num_clauses + 1)
        self.num_cols = 3 + (2 * puzzle.num_vars)

        # Create bottom 3 rows & top 2 rows of puzzle
        # Remaining area, including frame, is made of 'hard' blocks
        grid = self.build_frame()

        # Place gadgets to construct puzzle
        self.build_clauses(grid, puzzle)

        return grid

    # reduce helper function: create static areas of the grid that depend only on instance size
    def build_frame(self):
        assignment_row = 2
        # Column with path ('ladder's) between areas
        transition_col = self.num_cols - 2
        # Initially set entire zone to indestructible blocks
        # Using this "*" notation twice doesn't produce expected results
        #   because Python just makes pointers to original tuple
        grid = [[Block('hard')] * self.num_cols for row in range(self.num_rows)]

        # Starting zone
        for i in range(self.player.col, transition_col):
            grid[self.player.row][i] = Block('support')
        grid[self.player.row][transition_col] = Block('ladder')
        for i in range(self.player.col, transition_col - 1, 2):
            grid[assignment_row][i] = Block('soft')
        grid[assignment_row][transition_col] = Block('ladder')

        # Ending zone
        grid[self.num_rows - 2][transition_col] = Block('princess')
        # Stop princess from walking
        grid[self.num_rows - 3][transition_col] = Block('soft')

        # Send back partially-built level
        return grid

    # reduce helper function
    def build_clauses(self, grid, puzzle):
        row_pointer = 3

        for clause in range(puzzle.num_clauses):

            # Fill in gadget region for each variable for current tuple
            self.place_gadget(grid, puzzle.expanded_form[clause], row_pointer)
            row_pointer += GADGET_HEIGHT

    # reduce helper function
    def place_gadget(self, grid, variable_states, bottom_row):
        start_col = 2
        # Column with path ('ladder's) between areas
        transition_col = self.num_cols - 2

        # Create transition to next zone
        grid[bottom_row][transition_col] = Block('ladder')
        grid[bottom_row + 1][transition_col] = Block('support')
        # state[bottom_row + 2][transition_col] is already 'hard'
        grid[bottom_row + 3][transition_col] = Block('ladder')
        grid[bottom_row + 4][transition_col] = Block('ladder')
        grid[bottom_row + 5][transition_col] = Block('ladder')

        # Carve out walkable area, skipping gadget columns
        for i in range(start_col, transition_col, 2):
            grid[bottom_row + 1][i] = Block('support')
            grid[bottom_row + 3][i] = Block('support')
            grid[bottom_row + 4][i] = Block('support')

        # Place 'ladder's according to gadget structure
        for var_index in range(len(variable_states)):
            self.place_sub_gadget(
                grid, variable_states[var_index], bottom_row + 1, 2 * var_index + 1)

    # reduce helper function: place a part of a gadget corresponding to the state of 1 variable
    def place_sub_gadget(self, grid, var_state, bottom_row, col):
        for i in range(SUB_GADGET_HEIGHT):
            grid[bottom_row + i][col] = Block(SUB_GADGETS[var_state + 1][i])

    # compute the popils-specific solving move sequence for the given 3SAT instance
    def solve(self, puzzle):
        steps = []
        # make variable assignments
        for truthiness in puzzle.solution:
            if truthiness == 1:
                steps.append(UP)
            steps.append(RIGHT)
            steps.append(RIGHT)
        # traverse level
        for clause in range(puzzle.num_clauses):
            steps.append(UP)
            steps.append(UP)
            steps.append(UP)

            satisfied = puzzle.satisfied_vars(
                puzzle.three_sat[clause], puzzle.solution)
            closest = max([abs(var) for var in satisfied])
            lateral_blocks = 2 * (puzzle.num_vars + 1 - closest)

            # move to nearest viable 'ladder'
            for i in range(lateral_blocks):
                steps.append(LEFT)
            # climb to next clause
            steps.append(UP)
            steps.append(UP)
            # go back to the main 'ladder'
            for i in range(lateral_blocks):
                steps.append(RIGHT)
            # get in position to traverse the next clause
            steps.append(UP)

        # climb to princess!
        steps.append(UP)
        steps.append(UP)
        steps.append(UP)

        return steps

    # vector is one of the common vectors imported from common_constants
    def update(self, vector):
        vertical = 0
        horizontal = 1
        target = self.grid[self.player.row + vector[vertical]
                        ][self.player.col + vector[horizontal]]
        if vector == UP:
            if target.type == 'soft':
                for falling_row in range(self.player.row + 1, self.num_rows - 1):
                    self.grid[falling_row][self.player.col] = self.grid[falling_row + 1][self.player.col]
                self.grid[self.num_rows - 1][self.player.col] = Block('hard')
                self.altered_rows = [self.player.row + 1, self.num_rows - 1]
                self.altered_cols = [self.player.col, self.player.col]
            elif self.grid[self.player.row][self.player.col].type == 'ladder' and (target.type != 'hard'):
                self.move(UP)
        elif target.type != 'hard':
            self.move(vector)
            while (self.grid[self.player.row - 1][self.player.col].type == 'support' and self.grid[self.player.row][self.player.col].type == 'support'):
                self.move(DOWN)

    # update helper
    def move(self, vector):
        vertical = 0
        horizontal = 1

        self.altered_rows = [self.player.row, self.player.row]
        self.altered_cols = [self.player.col, self.player.col]

        self.player.row += vector[vertical]
        self.player.col += vector[horizontal]

        if self.grid[self.player.row][self.player.col].type == 'princess':
            self.complete = True