from abc import ABC, abstractmethod

from common_constants import UP, DOWN, LEFT, RIGHT, ZERO



class Game(ABC):  # tile-based game, either popils or megalit
    @abstractmethod
    def solve(self, puzzle):
        pass

    #
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
        self.solution = self.generate_solution(puzzle)


# this class will populate the game grid
class Block():
    def __init__(self, color, traversable=False, repulsion_force=DOWN, connectivity=[ZERO], destructible=False):
        self.color = color
        self.traversible = traversable
        self.repulsion_force = repulsion_force
        self.connectivity = connectivity
        self.destructible = destructible


class Air(Block):
    def __init__(self, color):
        super().__init__(color, traversable=True, connectivity=[])

class Scaffold(Block):
    def __init__(self, color):
        super().__init__(color, traversable=True)

class Ladder(Block):
    def __init__(self, color):
        super().__init__(color, traversable=True, repulsion_force=ZERO)


# wrapper class to track player position
class Player():
    def __init__(self, pos):
        self.row = pos[0]
        self.col = pos[1]
        self.color = (255, 0, 0)  # red
