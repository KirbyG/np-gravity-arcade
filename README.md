# Reducing 3SAT to Gravity-based Arcade Games
We have developed a novel proof technique for demonstrating NP-completeness of
simple arcade games that rely on gravity as a primary mechanic. This project
supports [this paper](https://www.researchgate.net/publication/361912480_Unstacking_Slabs_Safely_in_Megalit_is_NP-Hard) that applies the technique to the games [Popils](https://www.youtube.com/watch?v=2c5qgU0tvlk)
and [Megalit](https://www.youtube.com/watch?v=kWxrch10dWA).

## Usage
```
./np-gravity.py [-h] [-f FILENAME] [-s] [-m]

optional arguments:
  -h, --help     show this help message and exit
  -f FILENAME    file containing an instance of 3SAT in DIMACS CNF format
  -m, --megalit  reduce 3SAT to Megalit instead of Popils
  -q, --quick    Increase game speed. Useful for playing back long autosolves
  -s, --solve    run puzzle auto-solver
```

For example, `./np-gravity -m -s` reduces "default.cnf" to *Megalit*
and auto-solves the generated level. `./np-gravity -f examples/unsolvable.cnf`
reduces "examples/unsolvable.cnf" to *Popils* and generates an interactive level.

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

## References
* [3SAT Example Library](https://www.cs.ubc.ca/%7Ehoos/SATLIB/benchm.html)
* [Megalit Reduction Concept](https://docs.google.com/spreadsheets/d/1xu297SNoUu8qFG4eRkkXsX5r0zjv5CCPZEqo3ZCrlRM/edit?usp=sharing)
* [*Popils* Wiki Entry](https://en.wikipedia.org/wiki/Popils) 
	/ [Popils Gameplay](https://www.youtube.com/watch?v=wsvmqVdh3Do)
* [*Megalit* Wiki Entry](https://en.wikipedia.org/wiki/Megalit) 
	/ [Megalit Gameplay](https://www.youtube.com/watch?v=2ccKBg8pZXk)

## Related Papers
* [Gaming is a hard job, but someone has to do it!](https://arxiv.org/abs/1201.4995)
* [Classic Nintendo Games are (Computationally) Hard](https://arxiv.org/abs/1203.1895)
* [Block Dude Puzzles are NP-Hard (and the Rugs Really Tie the Reductions Together)](https://www.researchgate.net/publication/352934749_Block_Dude_Puzzles_are_NP-Hard_and_the_Rugs_Really_Tie_the_Reductions_Together) 

# TODOs
* I don't think the sim uses the updated var setter gadget
* add speed setting for autosolve mode
* port from PyGame (python3) to Pico-8 (Lua)
* host game on Aaron's website
