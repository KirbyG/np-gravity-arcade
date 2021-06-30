# this file contains the Megalit class and its Slab helper class

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

        # initialize to air blocks
        self.grid = Grid(20, 11, lambda: Block('air'))

        # bottom and top
        for x in range(self.grid.dim.x):
            self.grid[x, 0].type = 'border'
            self.grid[x, self.grid.dim.y - 1].type = 'border'

        # sides
        for y in range(self.grid.dim.y):
            self.grid[0, y].type = 'border'
            self.grid[self.grid.dim.x - 1, y].type = 'border'

        # container for all slabs in the level
        self.slabs = []

        # left structure
        self.slabs.append(Slab(self.grid, Vector(6, 1), Vector(4, 0)))
        self.slabs.append(Slab(self.grid, Vector(6, 2), Vector(0, 2)))
        self.slabs.append(Slab(self.grid, Vector(6, 4), Vector(3, 0)))
        self.slabs.append(Slab(self.grid, Vector(7, 5), Vector(0, 2)))
        self.slabs.append(Slab(self.grid, Vector(7, 7), Vector(3, 0)))

        # right structure
        self.slabs.append(Slab(self.grid, Vector(12, 7), Vector(3, 0)))
        self.slabs.append(Slab(self.grid, Vector(14, 6), Vector(0, -2)))
        self.slabs.append(Slab(self.grid, Vector(14, 4), Vector(3, 0)))
        self.slabs.append(Slab(self.grid, Vector(16, 3), Vector(0, -2)))
        self.slabs.append(Slab(self.grid, Vector(16, 1), Vector(-4, 0)))
        
        # player start position
        self.player = Player(Vector(1, 1))
    
    # SOLVE - automatically generate the solution to the level

    def crawl_under_table(self, dir, table_width=3, splay=0):
        rev = -1 * dir
        leg_gap = ((table_width - 3) / 2) - splay

        # pull the first leg out from under the table
        self.solution.extend([dir] * leg_gap)
        self.solution.append(ZERO)
        self.solution.append([rev] * (leg_gap + 2))
        self.solution.append(ZERO)

        # climb over the first leg
        self.solution.append(UP)
        self.solution.extend([dir] * 2)

        # replace the first leg
        self.solution.append(ZERO)
        self.solution.extend([dir] * (leg_gap + 2))
        self.solution.append(ZERO)
        
        # push the second leg out from under the table
        self.solution.append(ZERO)
        self.solution.extend([dir] * (leg_gap + 2))

        # climb over the second leg
        self.solution.append(ZERO)
        self.solution.append(UP)
        self.solution.extend([dir] * 2)
        
        # replace the second leg
        self.solution.append(ZERO)
        self.solution.extend([rev] * (leg_gap + 2))
        self.solution.append(ZERO)

        # walk out from under the table
        self.solution.extend([dir] * leg_gap)

    # the solving move sequence for Megalit is significantly longer than for Popils
    def solve(self):
        self.solution =  []

        # set variables
        for setting in self.puzzle.solution:
            # approach the table
            self.solution.extend([RIGHT] * 2)

            # drop the tower if necessary
            if setting == 1:
                self.solution.append(UP)
                self.solution.extend([RIGHT] * 2)
                self.solution.append(ZERO)
                self.solution.append(LEFT)
                self.solution.append(ZERO)
                self.solution.append(LEFT)
            
            # crawl under the table
            self.crawl_under_table(table_width=5)
            
            # approach the climbing tower
            self.solution.extend([RIGHT] * 3)

            # crawl under the climbing tower
            self.crawl_under_table(table_width=19, splay=2)

            # get in position for the next iteration
            self.solution.append(RIGHT)

        # climb onto the first level of the tower

        # steal a table leg for use as a trampoline
        self.solution.extend([RIGHT] * 3)
        self.solution.append(ZERO)
        self.solution.extend([LEFT] * 4)
        self.solution.append(ZERO)
        self.solution.append(UP)
        self.solution.extend([RIGHT] * 2)
        self.solution.append(ZERO)
        self.solution.append(LEFT)
        self.solution.append(ZERO)
        
        # jump on the trampoline
        self.solution.extend([UP, LEFT] * 2)

        # establish position tracking variables
        tower = self.puzzle.num_clauses - 2
        side = RIGHT

        # solve each clause
        for clause in self.puzzle.expanded_form:
            # get to the main floor

            # crawl under the support table
            self.solution.extend([-1 * side] * 2)
            self.crawl_under_table(LEFT)

            # 

    # UPDATE - support gameplay

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
        if self.player.gripping:
            self.grid[self.player.pos + self.player.gripping].type = 'tip'
            self.player.gripping = ZERO
        else:
            if self.grid[self.player.pos + LEFT].type == 'tip':
                self.player.gripping = LEFT
                self.grid[self.player.pos + self.player.gripping].type = 'gripped'
            elif self.grid[self.player.pos + RIGHT].type == 'tip':
                self.player.gripping = RIGHT
                self.grid[self.player.pos + self.player.gripping].type = 'gripped'

    # move left or right unless blocked by a slab or level edge
    def walk(self, force):
        if self.grid[self.player.pos + force].type == 'air':
            self.player.pos += force
            self.player_fall()

    def update(self, force):
        if not force: # we are changing grip
            self.change_grip()
        elif self.player.gripping: # we are trying to move a slab
            if force.x: # we can ignore attempts to move up or down with a slab
                if self.grid[self.player.pos + force + DOWN].type != 'air' and not (self.player.gripping == -1 * force and self.grid[self.player.pos + force].type != 'air'): # ensure we have solid ground to move onto
                    slab = self.grid[self.player.pos + self.player.gripping].slab
                    moved, fell = slab.slide(force)

                    if moved: # the slab was able to move, so the player should as well
                        self.player.pos += force
                        
                        # end the game if a slab has fallen on the player
                        if self.grid[self.player.pos].type in ('slab', 'tip'):
                            self.complete = True

                        if fell: # our grip has been broken
                            self.player.gripping = ZERO
                            for block in slab.blocks:
                                if block.type == 'gripped':
                                    block.type = 'tip'

                        # end the game if all slabs are on the ground
                        if all([slab.grounded() for slab in self.slabs]):
                            self.complete = True

        else: # we are just trying to move
            if force == DOWN:
                self.player_fall()
            if force == UP:
                self.jump()
            if force.x:
                self.walk(force)

# keep track of Megalit slabs and support their motion and collapse mechanics
class Slab:
    # create a slab with the specified position and add it to the grid
    def __init__(self, grid, origin, extent):
        step = extent.normalize()
        self.world = grid
        self.blocks = []
        self.positions = []
        max_offset =  int(extent.magnitude) - 1
        for offset in range(max_offset + 1):
            position = origin + (offset * step)
            grid[position] = Block('tip' if offset in (0, max_offset) else 'slab', self)
            self.blocks.append(grid[position])
            self.positions.append(position)
        end = origin + ((extent.magnitude - 1) * step)
        grid[end] = Block('tip', self)

    def dirmost(self, dir):
        return abs(max([position @ dir for position in self.positions]))

    def grounded(self):
        return self.dirmost(DOWN) == 1

    def supported(self):
        return not all([self.world[position + DOWN].type == 'air' for position in self.positions if position.y == self.dirmost(DOWN)])

    def move(self, dir):
        vacated = [position for position in self.positions]
        self.positions = [position + dir for position in self.positions]
        for _, position in enumerate(self.positions):
            self.world[position] = self.blocks[_]
        need_air = [position for position in vacated if not position in self.positions]
        for position in need_air:
            self.world[position] = Block('air')

    # recursive
    def fall(self):
        upper_neighbors = [self.world[position + UP].slab for position in self.positions if position.y == self.dirmost(UP) and self.world[position + UP].slab]

        # drop this slab
        if not self.supported():
            self.move(DOWN)

        if not self.supported():
            for x in range(self.world.dim.x):
                for y in range (self.world.dim.y):
                    self.world[x, y].type = 'slab'
            return

        [neighbor.fall() for neighbor in upper_neighbors]

    # the player has tried to move this slab
    def slide(self, force):
        if all([self.world[position + force].type == 'air' for position in self.positions if position.x == self.dirmost(force)]):
            dropped = self.world[self.dirmost(-1 * force), self.dirmost(UP) + 1].slab
            self.move(force)
            # if this slab sliding removed the support for another slab, apply gravity to that slab with potential recursive consequences
            if dropped:
                dropped.fall()
            # apply gravity to self, which may also trigger a recursive collapse
            fell = not self.supported()
            self.fall()
            
            return True, fell
        return False, False
