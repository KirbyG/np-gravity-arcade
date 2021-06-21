from common_constants import VARS_PER_CLAUSE

# Default 3SAT instance. Will be ignored if user provides alternative
DEFAULT_3SAT = '1 2 3 -2 -3 4 1 -3 6 -1 4 5 2 -4 -6'


class Puzzle:
    def __init__(self, raw_instance):
        self.three_sat = self.parse(raw_instance)
        self.num_clauses = len(self.three_sat)
        self.expanded_form = self.expand()
        self.solution = self.find_solution()

    def expand(self):
        expansion = []
        for i, clause in enumerate(self.three_sat):
            expansion.append([])
            for var in range(self.num_vars):
                if var + 1 in clause:
                    expansion[i].append(1)
                elif -(var + 1) in clause:
                    expansion[i].append(-1)
                else:
                    expansion[i].append(0)
        return expansion

    def __repr__(self):
        return "CNF form of 3SAT: " + " ^ ".join(
            ["(" + " V ".join(clause) + ")" for clause in self.three_sat])

    def parse(self, raw_input):
        # Attempt to convert input to a list of integers
        try:
            array_form = [int(el) for el in str.split(raw_input)]
        except:
            print(
                "WARNING: Malformed input. Default 3SAT instance has been used instead.")
            array_form = [int(el) for el in str.split(DEFAULT_3SAT)]
        print(array_form)

        # Truncate input if there are variables that don't form a full clause
        extra_inputs = len(array_form) % VARS_PER_CLAUSE
        array_form = array_form[:len(array_form)-extra_inputs]
        if extra_inputs != 0:
            print(
                "WARNING: 3SAT requires tuples of exactly size 3. Input has been truncated appropriately.")

        # 2D representation of 3SAT problem (clauses contain vars)
        nested_form = [[array_form[VARS_PER_CLAUSE * i + j]
                        for j in range(VARS_PER_CLAUSE)] for i in range(int(len(array_form) / VARS_PER_CLAUSE))]
        print(nested_form)
        return self.convertToReducedForm(array_form, nested_form)

    def convertToReducedForm(self, array_form, nested_form):
        # Relabel variables to smallest possible numbers
        var_set = {abs(var) for var in array_form}
        self.num_vars = len(var_set)
        for index in range(1, self.num_vars + 1):
            if not index in var_set:
                to_relabel = min([elem for elem in var_set if elem <= index])
                var_set.discard(to_relabel)
                var_set.add(index)
                nested_form = [[index if var == to_relabel else var for var in clause]
                               for clause in nested_form]

        # Remove malformed clauses with duplicate vars
        reduced_form = [clause for clause in nested_form if len(
            {abs(var) for var in clause}) == VARS_PER_CLAUSE]

        return reduced_form

    def find_solution(self):
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

    # purely mathematical helper function mapping -R -> -1, R -> 1
    def _sign(self, num):
        return int(abs(num) / num)

    # given a clause and variable assignment, return the satisfied variables in that clause
    def satisfied_vars(self, clause, assignment):
        return [var for var in clause if assignment[abs(var) - 1] * self._sign(var) == 1]
