from common_constants import VARS_PER_CLAUSE


# #SAT instance container and associated methods
class Puzzle:
    def __init__(self, filepath):
        self.three_sat = self.parse(filepath)
        # num_clauses & num_vars are saved during parse()
        self.num_vars = int(self.num_vars)
        self.num_clauses = int(self.num_clauses)
        print("Reducing from: " + str(self))
        self.expanded_form = self.expand()
        self.solution = self.solve()

    # convert 3SAT to an expanded form useful in the popils and megalit reductions
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
        result = []
        str_three_sat = [[f"¬x{abs(var)}" if var < 0 else f"x{var}"
                          for var in clause]
                         for clause in self.three_sat]
        for clause in str_three_sat:
            vars = "(" + " ∨ ".join(clause) + ")"
            result.append(vars)
        return " ∧ ".join(result)

    def parse(self, filepath):
        with open(filepath) as file:
            raw_input = ""
            for line in file:
                line = line.strip()  # remove leading/trailing whitespace
                if line.startswith('c'):
                    # Ignore comment lines
                    continue
                elif line.startswith('p'):
                    # save problem info
                    _, _, self.num_vars, self.num_clauses = line.split()
                elif line.endswith('0'):
                    # process clause
                    raw_input += line[:-2] + " "  # Remove the zero
                else:
                    # Anything else is useless
                    continue

        # Convert input to a list of integers
        array_form = [int(el) for el in str.split(raw_input)]

        # Truncate input if there are variables that don't form a full clause
        extra_inputs = len(array_form) % VARS_PER_CLAUSE
        array_form = array_form[:len(array_form)-extra_inputs]
        if extra_inputs != 0:
            print(
                "WARNING: 3SAT requires tuples of exactly size 3. Input has been truncated appropriately.")

        # 2D representation of 3SAT problem (clauses contain vars)
        nested_form = [[array_form[VARS_PER_CLAUSE * i + j]
                        for j in range(VARS_PER_CLAUSE)] for i in range(int(len(array_form) / VARS_PER_CLAUSE))]
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

    def solve(self):
        possible_solutions = 2 ** self.num_vars
        # compute vector sequence
        # find the solving variable assignment by brute force
        for raw_guess in range(possible_solutions):
            print(f"Guess {raw_guess} / {possible_solutions}", end='\r')
            # Convert ordinal value of guess to its binary representation
            format_str = r'{:0' + str(self.num_vars) + r'b}'
            guess = [int(format_str.format(raw_guess)[j]) *
                     2 - 1 for j in range(self.num_vars)]

            # Save current solution guess iff
            # Every clause has at least one variable that 'passes'
            # Meaning it makes the value of the clause 'True'
            if all([not len(self.satisfied_vars(clause, guess)) == 0 for clause in self.three_sat]):
                truth_assignment = ["T" if val == 1 else "F" for val in guess]
                print("\n3SAT Solution found!")
                for i in range(len(truth_assignment)):
                    print(
                        f"x{i + 1} = {truth_assignment[i]}", end=", " if i != len(truth_assignment) - 1 else "", flush=True)
                return guess

        # If we made it here, none of the guesses were valid solutions to the problem
        return []

    # purely mathematical helper function mapping -R -> -1, R -> 1
    def sign(self, num):
        return int(abs(num) / num)

    # given a clause and variable assignment, return the satisfied variables in that clause
    def satisfied_vars(self, clause, assignment):
        return [var for var in clause if assignment[abs(var) - 1] * self.sign(var) == 1]
