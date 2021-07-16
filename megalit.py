# this file contains the Megalit class and its Slab helper class

from game import Game, Block, Player, Grid
from common_constants import LEFT, RIGHT, UP, DOWN, ZERO, Vector, sign
from math import floor, sqrt

# Megalit was developed by the ASCII Corporation for the Gameboy

# we use slab to refer to a 1 by x or x by 1 Megalit gameplay object


class Megalit(Game):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    # REDUCE - this is the heart of the NP-completeness proof

    def build_platform(self, bottom_center, width, height):
        bottom_left = bottom_center + (width - 1) / 2 * LEFT
        self.slabs.append(Slab(self.grid, bottom_left, width * RIGHT))
        if height > 1:
            for x in range(width):
                self.slabs.append(
                    Slab(self.grid, bottom_left + x * RIGHT, (height - 1) * UP))

    def build_table(self, bottom_center, width=3, height=3, splay=1):
        self.slabs.append(Slab(self.grid, bottom_center +
                          (splay + 1) / 2 * LEFT, (height - 1) * UP))
        self.slabs.append(Slab(self.grid, bottom_center +
                          (splay + 1) / 2 * RIGHT, (height - 1) * UP))
        self.slabs.append(Slab(self.grid, bottom_center + (height - 1)
                          * UP + (width - 1) / 2 * LEFT, width * RIGHT))

    def build_gadget(self, bottom_center, floor_height):
        self.build_platform(bottom_center, 9, floor_height)
        self.build_table(bottom_center + floor_height * UP, height=4)
        for y in range(13 - 4 - floor_height):
            self.build_platform(bottom_center + (9 + y) * UP, 9, 0)

    def magic(self, x):
        return round(((x + 2) * (x + 2) - (x + 2)) / 2) + 4

    def build_var_tower(self, var):
        # var setter area
        x = 6 + 30 * var
        self.build_table(Vector(x, 1), width=5)
        self.slabs.append(Slab(self.grid, Vector(x, 4), UP))
        self.slabs.append(Slab(self.grid, Vector(x, 5), 3 * UP))

        # top of level filler
        for y in range(self.grid.dim.y - 6, self.grid.dim.y - 1):
            self.slabs.append(Slab(self.grid, Vector(x - 4, y), 9 * RIGHT))

        # actual tower
        for clause in range(self.puzzle.num_clauses):
            self.build_gadget(Vector(x, 8 + 13 * clause),
                              self.magic(self.puzzle.expanded_form[clause][var]))

    def build_climbing_story(self, bottom_center, crunch=False):
        self.build_table(bottom_center, width=17, splay=5)
        for y in range(3 - crunch):
            self.build_platform(bottom_center + (y + 3) * UP, 19, 1)
        y = 6 - crunch
        self.slabs.append(Slab(self.grid, bottom_center + y * UP, 5 * UP))
        self.build_table(bottom_center + y * UP + 5 * LEFT)
        self.build_table(bottom_center + y * UP + 5 * RIGHT)
        self.build_platform(bottom_center + (y + 3) * UP + 6 * LEFT, 9, 4)
        self.build_platform(bottom_center + (y + 3) * UP + 6 * RIGHT, 9, 4)

    def build_climbing_tower(self, bottom_center):
        # var setter area
        self.build_climbing_story(bottom_center, crunch=True)

        # actual tower
        for story in range(self.puzzle.num_clauses):
            self.build_climbing_story(bottom_center + 13 * story * UP)

    # refer to <paper-filename>.pdf for details
    def reduce(self):
        # for now, just build a static level to test game mechanics

        # initialize to air blocks
        self.grid = Grid(3 + (self.puzzle.num_vars - 1) * 21 + self.puzzle.num_vars * 9,
                         2 + 7 + 13 * self.puzzle.num_clauses + 5, lambda: Block('air'))

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

        # do the actual reduction

        # climbing towers
        for var in range(self.puzzle.num_vars - 1):
            self.build_climbing_tower(Vector(21 + 30 * var, 1))

        # var towers
        for var in range(self.puzzle.num_vars):
            self.build_var_tower(var)

        # player start position
        self.player = Player(Vector(1, 1))

    # SOLVE - automatically generate the solution to the level

    # move left or right along flat ground
    def travel(self, vector):
        self.solution.extend([vector.normalize()] * round(vector.magnitude))

    # just like travel, but we are taking a slab with us
    def move(self, vector):
        self.solution.append(ZERO)
        self.travel(vector)
        self.solution.append(ZERO)

    # move from one side of an upright slab to the other
    def super_knight(self, dir):
        self.solution.append(UP)
        self.travel(2 * dir)

    def climb_stairs(self, vector):
        self.solution.extend([UP, vector.normalize(), DOWN]
                             * round(vector.magnitude))

    def inswitch(self, dir, table_width=3, splay=1):
        leg_gap = (table_width - 2 - splay) / 2
        self.travel(leg_gap * dir)
        self.move(-(leg_gap + 2) * dir)
        self.super_knight(-1 * dir)
        self.move((leg_gap + 2) * dir)

    def outswitch(self, dir, table_width=3, splay=1):
        leg_gap = (table_width - 2 - splay) / 2
        self.move((leg_gap + 2) * dir)
        self.super_knight(dir)
        self.move(-(leg_gap + 2) * dir)
        self.travel(-leg_gap * dir)

    def use_tower(self, dir):
        self.super_knight(dir)
        self.travel(dir)
        self.move(-2 * dir)
        self.super_knight(dir)
        self.move(-2 * dir)
        self.climb_stairs(-1 * dir)
        self.super_knight(-1 * dir)

    def varcross(self, dir):
        self.super_knight(dir)
        self.travel(dir)
        self.crawl_under_table(dir)
        self.travel(3 * dir)

    # composite operation
    def crawl_under_table(self, dir, table_width=3, splay=1):
        # inswitch
        self.inswitch(dir, table_width=table_width, splay=splay)
        # cross
        self.travel(max(1, splay - 1) * dir)
        # outswitch
        self.outswitch(dir, table_width=table_width, splay=splay)

    def incross(self, dir):
        self.travel(2 * dir)
        self.inswitch(dir, table_width=17, splay=5)

    def outcross(self, dir):
        self.outswitch(dir, table_width=17, splay=5)
        self.travel(2 * dir)

    def gapcross(self, dir):
        self.super_knight(dir)
        self.super_knight(dir)

    # composite operation to cross a climbing tower
    def towercross(self, dir):
        self.incross(dir)
        self.gapcross(dir)
        self.outcross(dir)

    # the solving move sequence for Megalit is significantly longer than for Popils
    def solve(self):
        self.solution = []

        # set variables
        for setting in self.puzzle.solution:
            # approach the table
            self.travel(2 * RIGHT)

            # drop the tower if necessary
            if setting == 1:
                self.climb_stairs(RIGHT)
                self.travel(RIGHT)
                self.move(LEFT)
                self.travel(LEFT)

            # crawl under the table
            self.crawl_under_table(RIGHT, table_width=5)

            # approach the climbing tower
            self.travel(3 * RIGHT)

            # crawl under the climbing tower
            self.crawl_under_table(RIGHT, table_width=19, splay=2)

            # get in position for the next iteration
            self.travel(RIGHT)

        # climb onto the first level of the tower

        # steal a table leg for use as a trampoline
        self.travel(3 * RIGHT)
        self.move(4 * LEFT)
        self.super_knight(RIGHT)
        self.move(LEFT)

        # jump on the trampoline
        self.climb_stairs(2 * LEFT)

        # establish position tracking variables

        # which tower are we on
        tower = self.puzzle.num_clauses - 2

        # which side of the tower are we climbing in from
        side = RIGHT

        # solve each clause
        for _, clause in enumerate(self.puzzle.expanded_form):
            # get to the main floor

            # crawl under the support table
            self.travel(-2 * side)
            self.crawl_under_table(LEFT)

            # move the table leg into position for the jump
            self.move(-2 * side)
            self.super_knight(side)
            self.move(-1 * side)

            # climb onto the 1 x 5
            self.climb_stairs(-2 * side)

            # find the closest tower that we can use to escape
            target_tower = min([abs(var - 1 - tower) for var in self.puzzle.satisfied_vars(
                self.puzzle.three_sat[_], self.puzzle.solution)])

            # determine the direction of travel
            travel_dir = sign(target_tower - tower) * RIGHT

            self.super_knight(travel_dir)
            self.outcross(travel_dir)
            side = travel_dir

            # now we loop until we are in position
            while tower + ((side.x + 1) / 2) != target_tower:
                self.varcross(travel_dir)
                self.towercross(travel_dir)
                tower += travel_dir.x

            self.use_tower(travel_dir)

        # self.use_mineshaft(side)

        # run across to the bulldozer

        # bulldozer operation loop
        while False:
            # loop up the bulldozer arms pushing them in as far as possible until we can remove a slab from the haunted house
            # pull the targeted slab into position above the trash compactor
            # loop back down the bulldozer arms
            # climb back over the bulldozer
            # operate the trash compactor
            # push the targeted slab to the end of the dump
            # climb back over the trash compactor
            # reset the trash compactor
            # climb out of the garbage zone
            # climb back over the bulldozer
            # reset the bulldozer
            # move to the base of the bulldozer
            pass

        # dismantle the bulldozer

    # UPDATE - support gameplay

    def player_fall(self):
        while self.grid[self.player.pos + DOWN].type == 'air':
            self.player.pos += DOWN

    def jump(self):
        # no double jumps ):
        if self.grid[self.player.pos + DOWN].type != 'air':
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
                self.grid[self.player.pos +
                          self.player.gripping].type = 'gripped'
            elif self.grid[self.player.pos + RIGHT].type == 'tip':
                self.player.gripping = RIGHT
                self.grid[self.player.pos +
                          self.player.gripping].type = 'gripped'

    # move left or right unless blocked by a slab or level edge
    def walk(self, force):
        if self.grid[self.player.pos + force].type == 'air':
            self.player.pos += force
            self.player_fall()

    def update(self, force):
        if not force:  # we are changing grip
            self.change_grip()
        elif self.player.gripping:  # we are trying to move a slab
            if force.x:  # we can ignore attempts to move up or down with a slab
                # ensure we have solid ground to move onto
                if self.grid[self.player.pos + force + DOWN].type != 'air' and not (self.player.gripping == -1 * force and self.grid[self.player.pos + force].type != 'air'):
                    slab = self.grid[self.player.pos +
                                     self.player.gripping].slab
                    moved, fell = slab.slide(force)

                    if moved:  # the slab was able to move, so the player should as well
                        self.player.pos += force

                        # end the game if a slab has fallen on the player
                        if self.grid[self.player.pos].type in ('slab', 'tip'):
                            self.complete = True

                        if fell:  # our grip has been broken
                            self.player.gripping = ZERO
                            for block in slab.blocks:
                                if block.type == 'gripped':
                                    block.type = 'tip'

                        # end the game if all slabs are on the ground
                        if all([slab.grounded() for slab in self.slabs]):
                            self.complete = True

        else:  # we are just trying to move
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
        max_offset = int(extent.magnitude) - 1
        for offset in range(max_offset + 1):
            position = origin + (offset * step)
            grid[position] = Block('tip' if offset in (
                0, max_offset) else 'slab', self)
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
        need_air = [
            position for position in vacated if not position in self.positions]
        for position in need_air:
            self.world[position] = Block('air')

    # recursive
    def fall(self):
        upper_neighbors = [self.world[position + UP].slab for position in self.positions if position.y ==
                           self.dirmost(UP) and self.world[position + UP].slab]

        # drop this slab
        if not self.supported():
            self.move(DOWN)

        if not self.supported():
            for x in range(self.world.dim.x):
                for y in range(self.world.dim.y):
                    self.world[x, y].type = 'slab'
            return

        [neighbor.fall() for neighbor in upper_neighbors]

    # the player has tried to move this slab
    def slide(self, force):
        if all([self.world[position + force].type == 'air' for position in self.positions if position.x == self.dirmost(force)]):
            dropped = self.world[self.dirmost(-1 * force),
                                 self.dirmost(UP) + 1].slab
            self.move(force)
            # if this slab sliding removed the support for another slab, apply gravity to that slab with potential recursive consequences
            if dropped:
                dropped.fall()
            # apply gravity to self, which may also trigger a recursive collapse
            fell = not self.supported()
            self.fall()

            return True, fell
        return False, False
