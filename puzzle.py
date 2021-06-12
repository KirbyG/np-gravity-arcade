import common_constants as const


class Puzzle:
    def __init__(self, three_sat):
        self.three_sat = three_sat
        self.num_clauses = len(three_sat)
        self.num_vars = len({abs(var) for var in three_sat})
        self.expanded_form = []
        self.solution = self._findSolution()

    def _findSolution(self):
        # compute vector sequence
        # find the solving variable assignment by brute force
        for raw_guess in range(2 ** self.num_vars):
            # Convert ordinal value of guess to its binary representation
            format_str = r'{:0' + str(self.num_vars) + r'b}'
            guess = [int(format_str.format(raw_guess)[j]) *
                            2 - 1 for j in range(self.num_vars)]

            # Save current solution guess iff
            # Every clause has at least one variable that 'passes'
            # Meaning it makes the value of the clause 'True'
            if all([not len(self.satisfied_vars(clause, guess)) == 0 for clause in self.three_sat]):
                return guess

        # If we made it here, none of the guesses were valid solutions to the problem
        return []

    # Returns the product of variable state (-1, 0, or 1) and variable truth setting (-1 or 1)
    def passes(self, var, guess):
        return self._sign(var) * guess[abs(var) - 1] == 1

    # Map num to -1, 0, or 1 (Negated, Absent, Present)
    def _sign(self, num):
        return int(abs(num) / num)

    def satisfied_vars(self, clause, assignment):
        return [var for var in clause if assignment[abs(var) - 1] * self._sign(var) == 1]
