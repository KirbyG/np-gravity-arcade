from abc import ABC, abstractmethod
from common import COLORS, ZERO
import numpy as np

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


# this class will populate the game grid
class Block():
    def __init__(self, type, slab=None, short_sides=None):
        self.type = type
        self.slab = slab
        self.short_sides = short_sides

    # TODO: this at least needs comments lol
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
        self.gripping = ZERO