from game import Game, Block, Player
from common_constants import UP

# Megalit was developed by the ASCII Corporation for the Gameboy
class Megalit(Game):
    # instantiate the level
    def __init__(self, puzzle):
        super().__init__(puzzle)

    # compute the solving move sequence
    def solve(self, puzzle):
        return [UP]

    # build a slab between the specified endpoints
    def build_slab(self, grid, endpoints):
        dir
        grid[endpoints[0][0]][endpoints[0][1]] = Block('slab', connections=)

    # build the level by reduction from puzzle
    def reduce(self, puzzle):
        # for now, just build a static level to test basic mechanics
        self.num_rows = 11
        self.num_cols = 20
        grid = [[Block('air') for col in range(self.num_cols)] for row in range(self.num_rows)]
        for row in range(self.num_rows):
            grid[row][0] = Block('border')
            grid[row][self.num_cols - 1] = Block('border')
        for col in range(self.num_cols):
            grid[0][col] = Block('border')
            grid[self.num_rows - 1][col] = Block('border')
        
        self.player = Player([1, 1])

    # update the gamestate based on a movement command
    def update(self, vector):
        pass
