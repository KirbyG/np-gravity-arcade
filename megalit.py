# this file contains the Megalit class and its Slab helper class

import builtins
from game import Game, Block, Player
from common_constants import LEFT, RIGHT, UP, DOWN, ZERO, Vector, Grid
from math import sqrt

# Megalit was developed by the ASCII Corporation for the Gameboy

# we use slab to refer to a 1 by x or x by 1 Megalit gameplay object

# see https://www.youtube.com/watch?v=2ccKBg8pZXk for gameplay footage
# or https://en.wikipedia.org/wiki/Megalit for a general overview

class Megalit(Game):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    # REDUCE - this is the heart of the NP-completeness proof

    # refer to <paper-filename>.pdf for details
    def reduce(self):
        # for now, just build a static level to test game mechanics
        grid = Grid(20, 11, lambda: Block('air'))
        for x in range(self.grid.dim.x):
            grid[x, 0].type = 'border'
            grid[x, self.grid.dim.y - 1].type = 'border'
        for y in range(self.grid.dim.y):
            grid[0, y].type = 'border'
            grid[self.grid.dim.x - 1, y].type = 'border'
        self.slabs = []
        self.slabs.append(Slab(grid, Vector(4, 1), Vector(2, 0)))
        self.build_slab(grid, Vector(6, 1), Vector(0, 2))
        self.build_slab(grid, Vector(8, 1), Vector(0, 2))
        self.build_slab(grid, Vector(5, 3), Vector(3, 0))
        self.build_slab(grid, Vector(6, 4), Vector(0, 2))
        self.build_slab(grid, Vector(5, 6), Vector(3, 0))
        self.player = Player([1, 1])
        return grid
    
    # SOLVE - automatically generate the solution to the level

    # the solving move sequence for Megalit is significantly longer than for Popils
    def solve(self):
        return [UP]

    # UPDATE - sUPport gameplay

    def player_fall(self):
        while self.grid[self.player.pos + DOWN].type == 'air':
            self.player.pos += DOWN

    def jump(self):
        if self.grid[self.player.pos + DOWN].type != 'air': # no double jumps ):
            jump_height = 0
            max_jump_height = 3
            # stop when we hit a ceiling or max jump height
            while self.grid[self.player.pos + UP].type == 'air' and jump_height < max_jump_height:
                self.player.pos += UP
                jump_height += 1

    # user has pressed the space bar to grip or release a slab
    def change_grip(self):
        pass

    # move LEFT or right unless blocked by a slab or level edge
    def walk(self, force):
        pass

    # TODO test level that is solvable without unphysical jumps, utilize slab class interface, then build actual slab class

    def update(self, vector):
        force = Vector(vector[1], vector[0])

        if self.player.gripping: # we are trying to move a slab
            if force.x: # we can ignore attempts to move UP or DOWN with a slab
                # this call may trigger a cascading collapse of slabs
                moved, fell = self.get_slab(self.player.pos + self.player.gripping).apply(force)
                
                if moved: # the slab was able to move, so the player should as well
                    self.player.pos += force
                    
                    # end the game if a slab has fallen on the player
                    if self.grid[self.player.pos].type in ('slab', 'tip'):
                        self.complete = True

                    if fell: # our grip has been broken
                        self.player.gripping = ZERO
        elif force: # we are just trying to move
            if force == DOWN:
                self.player_fall()
            if force == UP:
                self.jump()
            if force.x:
                self.walk(force)
        else:
            self.change_grip()

# keep track of Megalit slabs and sUPport their motion and collapse mechanics
class Slab:
    # create a slab with the specified position and add it to the grid
    def __init__(self, grid, origin, extent):
        step = extent.normalize()
        grid[origin] = Block('tip', connections=[step])
        for offset in range(1, int(extent.magnitude) - 1):
            position = origin + (offset * step)
            grid[position] = Block('slab', connections=[step, -1 * step])
        end = origin + ((extent.magnitude - 1) * step)
        grid[end] = Block('tip', connections=[-1 * step])

    def supported(self, slab):
        if slab:
            if self.grid[slab[0]].connections[0].x:
                sUPported = False
                for elem in slab:
                    if self.grid[elem + DOWN].type != 'air':
                        sUPported = True
                return sUPported
            return self.grid[slab[0] + DOWN].type != 'air'
        return True

    # recursive
    def fall(self, grid):
        break_pass = True
        while not self.supported(slab):
            for elem in slab:
                self.grid[elem + DOWN].type = self.grid[elem].type
                self.grid[elem].type = 'air'
            if break_pass:
                break_pass = False
                for elem in slab:
                    candidate_slab = self.reconstruct_slab(elem + UP)
                    if not self.supported(candidate_slab):
                        self.slab_fall(candidate_slab)
            slab = [elem + DOWN for elem in slab]
        else:
            return break_pass

    def fall(self, grid, force):
        # precheck: ensure the player has solid ground to move onto and the slab is free to move
        
        # compute the extremal lateral extent of the slab
        edge_dist = max([abs(self.player.x - loc.x) for loc in slab])

        # select the subset of blocks in the slab lying at this extremum
        slab_edge = [loc for loc in slab if abs(self.player.x - loc.x) == edge_dist]

        # for each of these blocks, verify that there is air to the side
        blocked = all([self.grid[loc + force].type == 'air' for loc in slab_edge])

        if not blocked and self.grid[self.player.loc + force + DOWN] != 'air':
            # UPdate both grid and slab
            for loc in reversed(slab):
                self.grid[loc + force].type = self.grid[loc].type
                loc += force

            # trigger a potentially recursive collapse
            if self.slab_fall(slab):
                # slab_fall returns True if a collapse occurs
                self.player.gripping = False

    # the player has tried to move this slab
    def slide(self, grid, force):
        # check if the slab can slide
        # slide the slab
        # if this slab sliding removed the support for another slab, apply gravity to that slab with potential recursive consequences
        # apply gravity to self, which may also trigger a recursive collapse
        return moved, fell