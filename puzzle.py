from abc import ABC, abstractmethod
from popils_constants import *

class Puzzle(ABC): #tile-based game, either popils or megalit
    @abstractmethod
    def __init__(self, three_sat):
        #reduce three_sat to initial game matrix
        self.state = self.reduce_three_sat()
        self.num_vars = max([abs(var) for clause in self.three_sat for var in clause])
        self.num_clauses = len(three_sat)
        self.solution = self.solve_three_sat()
    
    # Render the designated portion of the display
    @abstractmethod
    def draw(self, bounds, screen):
        pass
    
    # Map num to -1, 0, or 1 (Negated, Absent, Present)
    def sign(self, num):
        return int(abs(num) / num)
    
    # Returns the product of variable state (-1, 0, or 1) and variable truth setting (-1 or 1)
    def passes(self, var, guess):
        return self.sign(var) * guess[abs(var) - 1] == 1
    
    def solve_three_sat(self):
        # compute vector sequence
        # find the solving variable assignment by brute force
        good_guess = []
        for guess in range(2 ** self.num_vars):
            # Convert ordinal value of guess to its binary representation
            format_str = r'{:0' + str(self.num_vars) + r'b}'
            parsed_guess = [int(format_str.format(guess)[j]) *
                            2 - 1 for j in range(self.num_vars)]
    
            # Save current solution guess iff
            # Every clause has at least one variable that 'passes'
            # Meaning it yields a viable path through the clause
            if all([any([self.passes(self.three_sat[clause][var], parsed_guess)
                        for var in range(VARS_PER_CLAUSE)]) for clause in range(self.num_clauses)]):
                good_guess = parsed_guess
    
        return good_guess
    
    @abstractmethod
    def reduce_three_sat(self):
        pass