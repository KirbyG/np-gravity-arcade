import builtins
from game import Game, Block, Player
from common_constants import UP, Vector, Grid
from math import sqrt

# Megalit was developed by the ASCII Corporation for the Gameboy
class Megalit(Game):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    def solve(self, puzzle):
        return [UP]

    def build_slab(self, grid, origin, extent):
        step = extent.normalize()
        grid[origin] = Block('slab', connections=[step])
        for offset in range(1, int(extent.magnitude) - 1):
            position = origin + (offset * step)
            grid[position] = Block('slab', connections=[step, -1 * step])
        end = origin + ((extent.magnitude - 1) * step)
        grid[end] = Block('slab', connections=[-1 * step])

    def reduce(self, puzzle):
        # for now, just build a static level to test game mechanics
        self.num_rows = 11
        self.num_cols = 20
        grid = Grid(self.num_rows, self.num_cols, lambda: Block('air'))
        for row in range(self.num_rows):
            grid[row][0] = Block('border')
            grid[row][self.num_cols - 1] = Block('border')
        for col in range(self.num_cols):
            grid[0][col] = Block('border')
            grid[self.num_rows - 1][col] = Block('border')
        self.build_slab(grid, Vector(4, 1), Vector(2, 0))
        self.build_slab(grid, Vector(6, 1), Vector(0, 2))
        self.build_slab(grid, Vector(8, 1), Vector(0, 2))
        self.build_slab(grid, Vector(5, 3), Vector(3, 0))
        self.build_slab(grid, Vector(6, 4), Vector(0, 2))
        self.build_slab(grid, Vector(5, 6), Vector(3, 0))
        self.player = Player([1, 1])
        return grid

    def update(self, vector):
        force = Vector(vector[0], vector[1])