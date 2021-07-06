# Reducing 3SAT to Gravity-based Arcade Games
We have developed a novel proof technique for demonstrating NP-completeness of
simple arcade games that rely on gravity as a primary mechanic. This project
supports an upcoming paper that applies the technique to the games *Popils*
and *Megalit*.

## Usage
```
./np-gravity.py [-h] [-f FILENAME] [-s] [-m]

optional arguments:
  -h, --help     show this help message and exit
  -f FILENAME    file containing an instance of 3SAT in DIMACS CNF format
  -s             run puzzle auto-solver
  -m, --megalit  reduce 3SAT to Megalit instead of Popils
```

## Notes
The `archive` folder contains the results of our original foray into proving
*Popils* was NP-Complete. `examples` contains the 3SAT instances we have used
for testing. 

Since this tool is designed around the 3SAT variant of Boolean Satisfiability,
all clauses will be truncated to their first 3 variables.

## DIMACS CNF Format
By convention, Boolean Satisfiability problems in conjunctive normal form (CNF)
have a `.cnf` extension, while the rest have a `.sat` extension.
DIMACS CNF follows the syntax:
```
c Comment goes here
c Maybe some metadata
c Last comment
p cnf num_vars num_clauses
1 2 3 0
-2 -3 4 0
...
-1 4 5 0
```
* Lines prefixed with a `c` are considered to be comments and are ignored
* The line prefixed with a `p` contains the problem information
	* Format: In this case, CNF
	* `num_vars`: The number of unique variables (in this case `5`)
	* `num_clauses`: The number of clauses (in this case `3`)
* Each remaining line is one clause with a delimiter of `0`
	(rather than the newline) technically ending the clause
	* The ellipsis is not itself valid syntax, but for the sake of brevity
		implies an arbitrary number of additional clauses
	* Minus signs denote negation of the attached variable
	* `0` is not a valid variable index

For example, the line `-1 4 5 0` is equivalent to the clause `(¬x1 V x4 V x5)`
where `¬` is the logical negation symbol.

## Resources
* [3SAT Example Library](https://www.cs.ubc.ca/%7Ehoos/SATLIB/benchm.html)
* [Megalit Reduction Concept](https://docs.google.com/spreadsheets/d/1xu297SNoUu8qFG4eRkkXsX5r0zjv5CCPZEqo3ZCrlRM/edit?usp=sharing)
* [*Popils* (for the Sega Game Gear)](https://en.wikipedia.org/wiki/Popils)
* [*Megalit* (for the Nintendo Game Boy)](https://en.wikipedia.org/wiki/Megalit)


# (Non-exhaustive) TODO List
### jacob
* add more example instances
* optimize input parsing logic

### kirby
* blocks can see their slabs
* scrolling
* class breakouts
* megalit
	* comment scrolling code
	* reduction (fix obvious issue first in g-sheets)
	* solver
### both
* fix Game repr
* allow exit during solve
* refactor code (comments and organization)
* write the actual paper
