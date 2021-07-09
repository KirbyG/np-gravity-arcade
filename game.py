from abc import ABC, abstractmethod
from common_constants import UP, DOWN, LEFT, RIGHT, ZERO, COLORS, Vector


# tile-based game, either popils or megalit
class Game(ABC):
    # subclasses must expose a method to generate a solving move sequence
    @abstractmethod
    def solve(self):
        pass

    # subclasses must expose a method to reduce 3SAT into a game level
    @abstractmethod
    def reduce(self):
        pass

    # returns the bounding box surrounding affected game-grid elements
    @abstractmethod
    def update(self, command):
        pass

    # compute and store the reduction and solving move sequence
    def __init__(self, puzzle):
        self.complete = False
        self.puzzle = puzzle
        self.reduce()  # build the grid
        self.solution = self.solve()  # build the solution
        self.solution_step = 0

    def __repr__(self):
        return repr(self.grid)


# wrapper for a 2d matrix allowing vector indexing
class Grid:
    def __init__(self, *args):
        if callable(args[-1]):
            initializer = args[-1]
            args = args[:-1]
        else:
            def initializer(): return None
        if len(args) == 1:
            self.dim = args[0]
        else:
            self.dim = Vector(args[0], args[1])
        self.grid = [[initializer() for y in range(self.dim.y)]
                     for x in range(self.dim.x)]

    def __getitem__(self, key):
        if type(key) == Vector:
            return self.grid[int(key.x)][int(key.y)]
        else:
            x, y = key
            return self.grid[int(x)][int(y)]

    def __setitem__(self, key, value):
        if type(key) == Vector:
            self.grid[int(key.x)][int(key.y)] = value
        else:
            x, y = key
            self.grid[int(x)][int(y)] = value

    def __repr__(self):
        result = ''
        transposed_grid = zip(*self.grid)

        for row in transposed_grid:
            for block in row[::-1]:  # flip output horizontally
                result += repr(block) + ' '
            result += '\n'
        return result[::-1]  # flip output vertically


# this class will populate the game grid. currently this is just a wrapper for a color
class Block():
    def __init__(self, type, slab=None):
        self.type = type
        self.slab = slab

    def __setattr__(self, name, value):
        if name == 'type':
            self.identity = value
            self.color = COLORS[self.identity]
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if name == 'type':
            return self.identity

    def __repr__(self):
        return self.type.upper()[0]


# wrapper class to track player position
class Player():
    def __init__(self, pos):
        self.pos = pos
        self.color = (255, 0, 0)  # red
        self.gripping = Vector(0, 0)
