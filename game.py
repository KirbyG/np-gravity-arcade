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
        self.sol = np.empty((0,2), dtype='int')
        self.solve()  # build the solution
        self.solution_step = 0

    def __repr__(self):
        return repr(self.grid)
