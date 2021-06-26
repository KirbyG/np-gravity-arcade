from abc import ABC, abstractmethod
from common_constants import UP, DOWN, LEFT, RIGHT, ZERO, COLORS, Vector

# tile-based game, either popils or megalit
class Game(ABC):
    # subclasses must expose a method to generate a solving move sequence
    @abstractmethod
    def solve(self, puzzle):
        pass

    # subclasses must expose a method to reduce 3SAT into a game level
    @abstractmethod
    def reduce(self, puzzle):
        pass

    # returns the bounding box surrounding affected game-grid elements
    @abstractmethod
    def update(self, command):
        pass

    # compute and store the reduction and solving move sequence
    def __init__(self, puzzle):
        self.complete = False
        self.altered_rows = self.altered_cols = [0, 0]
        self.grid = self.reduce(puzzle)
        self.solution = self.solve(puzzle)
        self.solution_step = 0
        self.altered_rows = [0, self.num_rows - 1]
        self.altered_cols = [0, self.num_cols - 1]

    def __repr__(self):
        result = ''
        for row in self.grid:
            for block in row:
                result += block.type + ' '
            result += '\n'
        return result

# this class will populate the game grid. currently this is just a wrapper for a color
class Block():
    def __init__(self, type, connections=[]):
        self.color = COLORS[type]
        self.type = type
        self.connections = connections

# wrapper class to track player position
class Player():
    def __init__(self, pos):
        self.row = pos[0]
        self.col = pos[1]
        self.color = (255, 0, 0)  # red

