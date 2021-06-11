from abc import ABC, abstractmethod

import common_constants as const


class Game(ABC):  # tile-based game, either popils or megalit
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.num_rows = 6 * (puzzle.num_clauses + 1)
        self.num_cols = 3 + (2 * puzzle.num_unique_vars)

    @abstractmethod
    def initSpecialAreas(self):
        pass

    @abstractmethod
    def initSatisfiabilityClauses(self):
        pass

    @abstractmethod
    def move(self, vector, player):
        pass

    @abstractmethod
    def force(self, vector, player):
        pass


class Block():
    def __init__(self, color, traversable, repulsion_force=const.DOWN, connectivity=[], destructible=False):
        pass
