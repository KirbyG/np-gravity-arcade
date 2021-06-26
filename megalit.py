import builtins
from game import Game, Block, Player
from common_constants import UP
from math import sqrt

# Megalit was developed by the ASCII Corporation for the Gameboy
class Megalit(Game):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    def solve(self, puzzle):
        return [UP]

    def build_slab(self, grid, origin, extent):
        step = extent.normalize()
        grid[origin.row][origin.col] = Block('slab', connections=[step])
        for offset in range(1, int(extent.magnitude) - 1):
            position = origin + (offset * step)
            grid[position.row][position.col] = Block('slab', connections=[step, -1 * step])
        end = origin + extent
        grid[end.row][end.col] = Block('slab', connections=[-1 * step])

    def reduce(self, puzzle):
        # for now, just build a static level to test game mechanics
        self.num_rows = 11
        self.num_cols = 20
        grid = [[Block('air') for col in range(self.num_cols)] for row in range(self.num_rows)]
        for row in range(self.num_rows):
            grid[row][0] = Block('border')
            grid[row][self.num_cols - 1] = Block('border')
        for col in range(self.num_cols):
            grid[0][col] = Block('border')
            grid[self.num_rows - 1][col] = Block('border')
        self.build_slab(grid, Vector(4, 1), Vector(2, 1))
        self.build_slab(grid, Vector(6, 1), Vector(1, 2))
        self.build_slab(grid, Vector(8, 1), Vector(1, 2))
        self.build_slab(grid, Vector(5, 3), Vector(3, 1))
        self.build_slab(grid, Vector(6, 4), Vector(1, 2))
        self.build_slab(grid, Vector(5, 6), Vector(3, 1))
        self.player = Player([1, 1])
        return grid

    def update(self, vector):
        force = Vector(vector[0], vector[1])
        # TODO game mechanics

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.magnitude = sqrt(self.x ** 2 + self.y ** 2)

    def __matmul__(self, other):
        return Vector(self.x * other.x, self.y * other.y)

    # pure function
    def normalize(self):
        return Vector(self.x / self.magnitude, self.y / self.magnitude)

    def __rmul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    # aliasing for convenient matrix access use cases
    def __getattr__(self, name):
        print(name)
        if name == 'row':
            return self.y
        if name == 'col':
            return self.x
        raise AttributeError