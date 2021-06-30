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
        result = ''
        for row in self.grid.grid[::-1]:
            for block in row:
                result += block.type.upper()[0] + ' '
            result += '\n'
        return result


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


# wrapper class to track player position
class Player():
    def __init__(self, pos):
        self.pos = pos
        self.color = (255, 0, 0)  # red
        self.gripping = Vector(0, 0)
