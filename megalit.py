# this file contains the Megalit class and its Slab helper class

from game import Game, Block, Player
from common_constants import LEFT, RIGHT, UP, DOWN, ZERO, Vector, Grid, sign
from math import floor, sqrt

# Megalit was developed by the ASCII Corporation for the Gameboy

# we use slab to refer to a 1 by x or x by 1 Megalit gameplay object


class Megalit(Game):
    def __init__(self, puzzle):
        super().__init__(puzzle)
        self.hover = 0
        self.hysteresis = LEFT

    # REDUCE - this is the heart of the NP-completeness proof

    def build_platform(self, bottom_left, width, height):
        self.slabs.append(Slab(self.grid, bottom_left, width * RIGHT))
        if height > 1:
            for x in range(width):
                self.slabs.append(
                    Slab(self.grid, bottom_left + x * RIGHT + UP, (height - 1) * UP))

    def build_table(self, bottom_center, width=3, height=3, splay=1):
        self.slabs.append(Slab(self.grid, bottom_center +
                          (splay + 1) / 2 * LEFT, (height - 1) * UP))
        self.slabs.append(Slab(self.grid, bottom_center +
                          (splay + 1) / 2 * RIGHT, (height - 1) * UP))
        self.slabs.append(Slab(self.grid, bottom_center + (height - 1)
                          * UP + (width - 1) / 2 * LEFT, width * RIGHT))

    def build_gadget(self, bottom_center, floor_height):
        self.build_platform(bottom_center + 4 * LEFT, 9, floor_height)
        self.build_table(bottom_center + floor_height * UP, height=4)
        for y in range(13 - 4 - floor_height):
            self.build_platform(
                bottom_center + (floor_height + 4 + y) * UP + 4 * LEFT, 9, 0)

    def magic(self, x):
        if x == 0:
            return 4
        if x == -1:
            return 5
        if x == 1:
            return 7

    def build_var_tower(self, var):
        # var setter area
        x = 6 + 32 * var
        self.build_table(Vector(x, 1), width=5)
        self.slabs.append(Slab(self.grid, Vector(x, 4), RIGHT))
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
        self.build_platform(bottom_center + 3 * UP + 8 * LEFT, 17, 1)
        for y in range(2 - crunch):
            self.build_platform(bottom_center + (y + 4) * UP + 9 * LEFT, 19, 1)
        y = 6 - crunch
        self.slabs.append(Slab(self.grid, bottom_center + y * UP, 5 * UP))
        self.build_table(bottom_center + y * UP + 5 * LEFT)
        self.build_table(bottom_center + y * UP + 5 * RIGHT)
        self.build_platform(bottom_center + (y + 3) * UP + 11 * LEFT, 10, 4)
        self.build_platform(bottom_center + (y + 3) * UP + 2 * RIGHT, 10, 4)

    def build_climbing_tower(self, bottom_center):
        # var setter area
        self.build_climbing_story(bottom_center, crunch=True)

        # actual tower
        for story in range(self.puzzle.num_clauses):
            self.build_climbing_story(bottom_center + (13 * story + 12) * UP)

    # refer to <paper-filename>.pdf for details
    def reduce(self):
        # for now, just build a static level to test game mechanics

        # initialize to air blocks
        self.grid = Grid(3 + (self.puzzle.num_vars - 1) * 23 + self.puzzle.num_vars * 9,
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
            self.build_climbing_tower(Vector(22 + 32 * var, 1))

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
        self.super_knight(dir)
        self.move((leg_gap + 2) * dir)

    def outswitch(self, dir, table_width=3, splay=1):
        leg_gap = (table_width - 2 - splay) / 2
        self.move((leg_gap + 2) * dir)
        self.super_knight(dir)
        self.move(-(leg_gap + 2) * dir)
        self.travel(leg_gap * dir)

    def use_tower(self, dir):
        self.super_knight(dir)
        self.travel(dir)
        self.move(-2 * dir)
        self.super_knight(dir)
        self.move(-2 * dir)
        self.climb_stairs(-1 * dir)
        self.super_knight(-1 * dir)

    def varcross(self, dir, setting):
        if setting == 1:
            self.super_knight(dir)
        else:
            self.travel(2 * dir)
        self.travel(dir)
        self.crawl_under_table(dir)
        self.travel(dir)
        if setting == 1:
            self.travel(2 * dir)
        else:
            self.super_knight(dir)

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
        for var, setting in enumerate(self.puzzle.solution):
            # approach the table
            self.travel(2 * RIGHT)

            # drop the tower if necessary
            if setting == 1:
                self.climb_stairs(RIGHT)
                self.travel(RIGHT)
                self.move(LEFT)
                self.travel(LEFT)

            if var != self.puzzle.num_vars - 1:
                # crawl under the table
                self.crawl_under_table(RIGHT, table_width=5)

                # approach the climbing tower
                self.travel(4 * RIGHT)

                # crawl under the climbing tower
                self.crawl_under_table(RIGHT, table_width=17, splay=5)

                # get in position for the next iteration
                self.travel(2 * RIGHT)

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
        tower = self.puzzle.num_vars - 1.5

        # which side of the tower are we climbing in from
        travel_dir = RIGHT

        # solve each clause
        for _, clause in enumerate(self.puzzle.expanded_form):
            # get to the main floor

            # crawl under the support table
            self.travel(-2 * travel_dir)
            self.inswitch(-1 * travel_dir)
            self.move(-3 * travel_dir)

            # climb onto the 1 x 5
            self.climb_stairs(-2 * travel_dir)

            # find the closest tower that we can use to escape
            target_tower = abs(self.puzzle.satisfied_vars(
                self.puzzle.three_sat[_], self.puzzle.solution)[0]) - 1

            # determine the direction of travel
            travel_dir = sign(target_tower - tower) * RIGHT

            self.super_knight(travel_dir)
            self.outcross(travel_dir)
            tower += 0.5 * travel_dir.x

            # now we loop until we are in position
            while round(tower) != target_tower:
                print(round(tower), target_tower)
                self.varcross(travel_dir, clause[round(tower)])
                self.towercross(travel_dir)
                tower += travel_dir.x
            self.use_tower(travel_dir)
            tower -= 0.5 * travel_dir.x

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
            self.hover = 2

    # user has pressed the space bar to grip or release a slab
    def change_grip(self):
        if self.player.gripping:
            self.grid[self.player.pos + self.player.gripping].type = 'tip'
            self.player.gripping = ZERO
        else:
            if self.grid[self.player.pos + self.hysteresis].type == 'tip':
                self.player.gripping = self.hysteresis
                self.grid[self.player.pos +
                          self.player.gripping].type = 'gripped'
            elif self.grid[self.player.pos + -1 * self.hysteresis].type == 'tip':
                self.player.gripping = -1 * self.hysteresis
                self.grid[self.player.pos +
                          self.player.gripping].type = 'gripped'

    # move left or right unless blocked by a slab or level edge
    def walk(self, force):
        self.hysteresis = force
        if self.grid[self.player.pos + force].type == 'air':
            self.player.pos += force
            self.hover -= 1
            if self.hover <= 0:
                self.player_fall()
                self.hover = 0

    def update(self, force):
        force = Vector(round(force.x), round(force.y))
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
            grid[position] = Block('slab', self, short_sides=[
                                   Vector(step.y, step.x), -1 * Vector(step.y, step.x)])
            if offset == 0:
                grid[position].type = 'tip'
                grid[position].short_sides.append(-1 * step)
            if offset == max_offset:
                grid[position].type = 'tip'
                grid[position].short_sides.append(step)
            self.blocks.append(grid[position])
            self.positions.append(position)
        end = origin + ((extent.magnitude - 1) * step)
        #grid[end] = Block('tip', self, short_sides=[Vector(step.y, step.x), -1 * Vector(step.y, step.x)])

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
        upper_neighbors = set([self.world[position + UP].slab for position in self.positions if position.y ==
                               self.dirmost(UP) and self.world[position + UP].slab])

        # drop this slab
        if not self.supported():
            self.move(DOWN)
            for neighbor in upper_neighbors:
                neighbor.fall()

        if not self.supported():
            for x in range(self.world.dim.x):
                for y in range(self.world.dim.y):
                    self.world[x, y].type = 'slab'
            return

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
