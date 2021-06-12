from abc import ABC, abstractmethod

import common_constants as const
from common_constants import UP, DOWN, LEFT, RIGHT

class Game(ABC):  # tile-based game, either popils or megalit
    @abstractmethod
    def generate_solution(self, puzzle):
        pass

    #
    @abstractmethod
    def reduce(self, puzzle):
        pass

    # compute and store the reduction and solving move sequence
    def __init__(self, puzzle):
        self.grid = self.reduce(puzzle)
        self.solution = self.generate_solution(puzzle)
        self.complete = False

    # returns the bounding box surrounding affected game-grid elements
    @abstractmethod
    def update(self, command):
        pass

# this class will populate the game grid
class Block():
    def __init__(self, color, traversable, repulsion_force=DOWN, connectivity=[], destructible=False):
        self.color = color
        self.traversible = traversable
        self.repulsion_force = repulsion_force
        self.connectivity = connectivity
        self.destructible = destructible

# wrapper class to track player position
class Player():
    #default player color
    PLAYER = (255, 0, 0)  # red

    def __init__(self, pos, color=PLAYER):
        self.row = pos[0]
        self.col = pos[1]
