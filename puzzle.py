import common_constants as const


class Puzzle:
    def __init__(self, three_sat):
        self.three_sat = three_sat
        self.num_clauses = len(three_sat)
        self.num_unique_vars = len({abs(var) for var in three_sat})
        self.solution = self._findSolution()

    def _findSolution(self):
        # compute vector sequence
        # find the solving variable assignment by brute force
        for guess in range(2 ** self.num_unique_vars):
            # Convert ordinal value of guess to its binary representation
            format_str = r'{:0' + str(self.num_unique_vars) + r'b}'
            parsed_guess = [int(format_str.format(guess)[j]) *
                            2 - 1 for j in range(self.num_unique_vars)]

            # Save current solution guess iff
            # Every clause has at least one variable that 'passes'
            # Meaning it makes the value of the clause 'True'
            if all([any([self._passes(self.three_sat[clause][var], parsed_guess)
                        for var in range(const.VARS_PER_CLAUSE)]) for clause in range(self.num_clauses)]):
                return parsed_guess

        # If we made it here, none of the guesses were valid solutions to the problem
        return []

    # Returns the product of variable state (-1, 0, or 1) and variable truth setting (-1 or 1)
    def _passes(self, var, guess):
        return self._sign(var) * guess[abs(var) - 1] == 1

    # Map num to -1, 0, or 1 (Negated, Absent, Present)
    def _sign(self, num):
        return int(abs(num) / num)
