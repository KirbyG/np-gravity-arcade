We have developed a novel proof technique for demonstrating NP-completeness of simple arcade games that rely on gravity as a primary mechanic. This project supports an upcoming paper (<paper-filename>.pdf) that applies the technique to Popils and Megalit. 

3SAT Example Library: https://www.cs.ubc.ca/%7Ehoos/SATLIB/benchm.html

TODO (jacob)
    remove manual cmd line entry
    adopt DIMACS CNF input format
    add input example to this file
    convert existing files to new format and .cnf extension
    Make README more useful

TODO (kirby)
    megalit
        reduction
            grip choice historesis
            allow superknight jumps
            fix the solver stub to manually fall
            add antimonkeybusiness potholes
            cut the corners
        solver

TODO (both)
    fix Game repr
    allow exit during solve
    refactor code (comments and organization)
        i'm forgetting what the design pattern is called, but i believe artist
        might be better as a draw function returned from a wrapper function
        that first instantiates all the constants and pygame resources. keeping
        this in its own module still seems desirable
    write the actual paper
