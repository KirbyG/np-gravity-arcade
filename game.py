from abc import ABC, abstractmethod

import common_constants as const
from common_constants import UP, DOWN, LEFT, RIGHT


class Game(ABC):  # tile-based game, either popils or megalit
   

    @abstractmethod
    def generate_solution(self, puzzle):
        pass

    @abstractmethod
    def reduce(self, puzzle):
        pass

    def __init__(self, puzzle):
        self.grid = self.reduce(puzzle)
        self.solution = self.generate_solution(puzzle)
        self.complete = False
        var = DOWN

    @abstractmethod
    def update(self, command):
        pass

class Block():
    def __init__(self, color, traversable, repulsion_force=const.DOWN, connectivity=[], destructible=False):
        self.color = color
        self.traversible = traversable
        self.repulsion_force = repulsion_force
        self.connectivity = connectivity
        self.destructible = destructible
