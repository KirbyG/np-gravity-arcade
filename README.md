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
            solver stub takes antimonkeybusiness potholes into account
            solver stub needs fewer steps to pass under the towers
            slab graphical clarity improvements
        solver

TODO (both)
    fix Game repr
    allow exit during solve
    refactor code (comments and organization)
        i'm forgetting what the design pattern is called, but i believe artist
        might be better as a draw function returned from a wrapper function
        that first instantiates all the constants and pygame resources. keeping
        this in its own module still seems desirable
    write the actual paper (we need to start by skimming a few other papers that do similar proofs. without seeing how others do it, the following would be my approach to the structure). clarity is probably the most important property to strive for. we also need sufficient rigor in the megalit proof in particular
        abstract
        introduction
            background on the idea behind proving games are in NP via reduction to level design (ie, what do we actually mean when we say a game is NP-complete)
        applications of the metatheorem
            popils
                background of the game, which features we use
                specifying the metatheorem gadgets
            megalit
                background of the game, what we assume is allowed (very long slabs, starting above the ground)
                specifying the metatheorem gadgets (trickier than for popils because we need to include a discussion of why the player can't cheat)
                the bulldozer cleanup phase
        metatheorem
            3SAT expanded form
            using gravity as the long range effect
            generalized schematic proof using abstract gadgets
        other stuff (???)
            references
            conclusion
            description of github project
            possibilities for extension
