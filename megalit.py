# this file contains the Megalit class and its Slab helper class

import builtins
from game import Game, Block, Player
from common_constants import LEFT, RIGHT, UP, DOWN, ZERO, left, right, up, down, zero, Vector, Grid
from math import sqrt

# Megalit was developed by the ASCII Corporation for the Gameboy

# we use slab to refer to a 1 by x or x by 1 Megalit gameplay object

# see https://www.youtube.com/watch?v=2ccKBg8pZXk for gameplay footage
# or https://en.wikipedia.org/wiki/Megalit for a general overview

class Megalit(Game):
    # we let Game handle __init__ calls

    # REDUCE - this is the heart of the NP-completeness proof

    # refer to <paper-filename>.pdf for details
    def reduce(self, puzzle):
        # for now, just build a static level to test game mechanics
        self.num_rows = 11
        self.num_cols = 20
        grid = Grid(self.num_rows, self.num_cols, lambda: Block('air'))
        for row in range(self.num_rows):
            grid[row][0] = Block('border')
            grid[row][self.num_cols - 1] = Block('border')
        for col in range(self.num_cols):
            grid[0][col] = Block('border')
            grid[self.num_rows - 1][col] = Block('border')
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
    def solve(self, puzzle):
        return [UP]

    # UPDATE - support gameplay

    def player_fall(self):
        while self.grid[self.player.pos + down].type == 'air':
            self.player.pos += down

    def jump(self):
        if self.grid[self.player.pos + down].type != 'air': # no double jumps ):
            jump_height = 0
            max_jump_height = 3
            # stop when we hit a ceiling or max jump height
            while self.grid[self.player.pos + up].type == 'air' and jump_height < max_jump_height:
                self.player.pos += up
                jump_height += 1

    # user has pressed the space bar to grip or release a slab
    def change_grip(self):
        pass

    # move left or right unless blocked by a slab or level edge
    def walk(self, force):
        pass

    # TODO test level that is solvable without unphysical jumps, utilize slab class interface, then build actual slab class

    def update(self, vector):
        force = Vector(vector[1], vector[0])

        if self.player.gripping: # we are trying to move a slab
            if force.x: # we can ignore attempts to move up or down with a slab
                # this call may trigger a cascading collapse of slabs
                moved, fell = self.get_slab(self.player.pos + self.player.gripping).apply(force)
                
                if moved: # the slab was able to move, so the player should as well
                    self.player.pos += force
                    
                    # end the game if a slab has fallen on the player
                    if self.grid[self.player.pos].type in ('slab', 'tip'):
                        self.complete = True

                    if fell: # our grip has been broken
                        self.player.gripping = zero
        elif force: # we are just trying to move
            if force == down:
                self.player_fall()
            if force == up:
                self.jump()
            if force.x:
                self.walk(force)
        else:
            self.change_grip()
        
        # for now, just redraw the entire game each loop                
        self.altered_rows = [0, self.num_rows - 1]
        self.altered_cols = [0, self.num_cols - 1]

# keep track of Megalit slabs and support their motion and collapse mechanics
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
                supported = False
                for elem in slab:
                    if self.grid[elem + down].type != 'air':
                        supported = True
                return supported
            return self.grid[slab[0] + down].type != 'air'
        return True

    # recursive
    def fall(self, grid):
        break_pass = True
        while not self.supported(slab):
            for elem in slab:
                self.grid[elem + down].type = self.grid[elem].type
                self.grid[elem].type = 'air'
            if break_pass:
                break_pass = False
                for elem in slab:
                    candidate_slab = self.reconstruct_slab(elem + up)
                    if not self.supported(candidate_slab):
                        self.slab_fall(candidate_slab)
            slab = [elem + down for elem in slab]
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

        if not blocked and self.grid[self.player.loc + force + down] != 'air':
            # update both grid and slab
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