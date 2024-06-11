# this file contains the Megalit class and its Slab helper class
from game import Game
from common import LEFT, RIGHT, UP, DOWN, ZERO
from common import _, sign
from common import X, Y
from common import AIR, BORDER
from common import JUGS, ROCKS
from common import ROCKBOTTOM, ROCKTOP, ROCKLEFT, ROCKRIGHT
from common import ROCKPOINT, ROCKCOLUMN, ROCKROW
import numpy as np

# each grid position needs to know what material it is and to which slab, if any, it
# belongs
BLOCK = 0
SLAB = 1

# Megalit was developed by the ASCII Corporation for the Gameboy

# we use slab to refer to a 1 by x or x by 1 Megalit gameplay object

class Megalit(Game):
    def __init__(self, puzzle):
        self.unsettled_slabs = 0
        super().__init__(puzzle)
        self.hover = 0
        self.facing = LEFT # track which way we have just moved for intuitive grabs
        self.grip = ZERO # ZERO for no grip, otherwise LEFT or RIGHT

########################################################################################

    # REDUCE - this is the heart of the NP-completeness proof see Megalit.pdf for
    # visuals
    def reduce(self):
        # initialize to air blocks
        self.grid = np.full(
            (
                (self.puzzle.num_vars - 1) * 23 + self.puzzle.num_vars * 9 + 10,
                2 + 7 + 13 * self.puzzle.num_clauses + 5
            ),
            AIR
        )

        # bottom and top
        self.grid[
            np.ix_(
                np.arange(self.grid.shape[X]),
                [0, self.grid.shape[Y] - 1]
            )
        ] = BORDER

        # sides
        self.grid[[0, self.grid.shape[X] - 1],:] = BORDER

        # do the actual reduction

        # climbing towers
        for var in range(self.puzzle.num_vars - 1):
            self.build_climbing_tower(np.array([22 + 32 * var, 1]))

        # var towers
        for var in range(self.puzzle.num_vars):
            self.build_var_tower(var)

        # player start position
        self.player = np.array([1, 1])

    def add_vertical_slab(self, origin, length):
        self.grid[_(origin)] = ROCKBOTTOM
        self.grid[origin[X], np.arange(1, length - 1) + origin[Y]]
        self.grid[_(origin + UP * length)] = ROCKTOP
    
    def add_horizontal_slab(self, origin, length):
        self.grid[_(origin)] = ROCKLEFT
        self.grid[np.arange(1, length - 1) + origin[X], origin[Y]]
        self.grid[_(origin + RIGHT * length)] = ROCKRIGHT

    # origin needs to be lower left
    def add_slab(self, origin, displacement):
        if displacement[X] + displacement[Y] == 1:
            self.grid[_(origin)] = ROCKPOINT
        else:
            if displacement[X] == 0:
                self.add_vertical_slab(origin, displacement[Y])
            else:
                self.add_horizontal_slab(origin, displacement[X])
        if origin[Y] > 1:
            self.unsettled_slabs += 1

    def build_platform(self, bottom_left, width, height):
        self.add_slab(bottom_left, width * RIGHT)
        if height > 1:
            for x in range(width):
                self.add_slab(bottom_left + x * RIGHT, (height - 1) * UP)

    def build_table(self, bottom_center, width=3, height=3, splay=1):
        self.add_slab(
            bottom_center + int((splay + 1) / 2) * LEFT,
            (height - 1) * UP
        )
        self.add_slab(
            bottom_center + int((splay + 1) / 2) * RIGHT,
            (height - 1) * UP
        )
        self.add_slab(
            bottom_center + (height - 1) * UP + int((width - 1) / 2) * LEFT,
            width * RIGHT
        )

    def build_gadget(self, bottom_center, floor):
        self.build_platform(bottom_center + 4 * LEFT, 9, floor)
        self.build_table(bottom_center + floor * UP, height=4)
        for y in range(13 - 4 - floor):
            self.build_platform(bottom_center + (floor + 4 + y) * UP + 4 * LEFT, 9, 0)

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
        self.build_table(np.array([x, 1]), width=5)
        self.add_slab(np.array([x, 4]), RIGHT)
        self.add_slab(np.array([x, 5]), 3 * UP)

        # top of level filler
        for y in range(self.grid.shape[Y] - 6, self.grid.shape[Y] - 1):
            self.add_slab(np.array([x - 4, y]), 9 * RIGHT)

        # actual tower
        for clause in range(self.puzzle.num_clauses):
            self.build_gadget(
                np.array([x, 8 + 13 * clause]),
                self.magic(self.puzzle.expanded_form[clause][var])
            )

    def build_climbing_story(self, bottom_center, crunch=False):
        self.build_table(bottom_center, width=17, splay=5)
        self.build_platform(bottom_center + 3 * UP + 8 * LEFT, 17, 1)
        for y in range(2 - crunch):
            self.build_platform(bottom_center + (y + 4) * UP + 9 * LEFT, 19, 1)
        y = 6 - crunch
        self.add_slab(bottom_center + y * UP, 5 * UP)
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

########################################################################################

    # SOLVE - automatically generate the solution to the level. The solving move
    # sequence for Megalit is significantly longer than for Popils
    def solve(self):
        if not self.puzzle.solution:
            print("INFO | Not running Megalit solver because 3SAT was not solved.")

        # set variables
        for var, setting in enumerate(self.puzzle.solution):
            # approach the table
            self.travel(RIGHT, 2)

            # drop the tower if necessary
            if setting == 1:
                self.climb_stairs(RIGHT, 1)
                self.travel(RIGHT, 3)
                self.move(LEFT, 1)
                self.travel(LEFT, 2)

            if var != self.puzzle.num_vars - 1:
                # crawl under the table
                self.crawl_under_table(RIGHT, table_width=5)

                # approach the climbing tower
                self.travel(RIGHT, 4)

                # crawl under the climbing tower
                self.crawl_under_table(RIGHT, table_width=17, splay=5)

                # get in position for the next iteration
                self.travel(RIGHT, 2)

        # climb onto the first level of the tower

        # steal a table leg for use as a trampoline
        self.travel(RIGHT, 3)
        self.move(LEFT, 4)
        self.super_knight(RIGHT)
        self.move(LEFT, 1)

        # jump on the trampoline
        self.climb_stairs(LEFT, 2)

        # establish position tracking variables

        # which tower are we on
        tower = self.puzzle.num_vars - 1.5

        # which side of the tower are we climbing in from
        travel_dir = RIGHT

        # solve each clause
        for _, clause in enumerate(self.puzzle.expanded_form):
            # get to the main floor

            # crawl under the support table
            self.travel(-travel_dir, 2)
            self.inswitch(-travel_dir)
            self.move(-travel_dir, 3)

            # climb onto the 1 x 5
            self.climb_stairs(-travel_dir, 2)

            # find the closest tower that we can use to escape
            target_tower = abs(self.puzzle.satisfied_vars(
                self.puzzle.three_sat[_], self.puzzle.solution)[0]) - 1

            # determine the direction of travel
            travel_dir = sign(target_tower - tower) * RIGHT

            self.super_knight(travel_dir)
            self.outcross(travel_dir)
            tower += 0.5 * travel_dir[X]

            # now we loop until we are in position
            while round(tower) != target_tower:
                print(round(tower), target_tower)
                self.varcross(travel_dir, clause[round(tower)])
                self.towercross(travel_dir)
                tower += travel_dir[X]
            self.use_tower(travel_dir)
            tower -= 0.5 * travel_dir[X]

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
            

    # move left or right along flat ground
    def travel(self, dir, dist):
        self.sol = np.vstack([self.sol, np.tile(dir, (dist, 1))])

    # just like travel, but we are taking a slab with us
    def move(self, dir, dist):
        self.sol = np.vstack([self.sol, ZERO])
        self.travel(dir, dist)
        self.sol = np.vstack([self.sol, ZERO])

    # move from one side of an upright slab to the other
    def super_knight(self, dir):
        self.sol = np.vstack([self.sol, UP])
        self.travel(dir, 2)

    def climb_stairs(self, dir, steps):
        self.sol = np.vstack([self.sol, np.tile([UP, dir, DOWN], (steps, 1))])

    def inswitch(self, dir, table_width=3, splay=1):
        leg_gap = int((table_width - 2 - splay) / 2) # ;)
        self.travel(dir, leg_gap)
        self.move(-dir, leg_gap + 2)
        self.super_knight(dir)
        self.move(dir, leg_gap + 2)

    def outswitch(self, dir, table_width=3, splay=1):
        leg_gap = int((table_width - 2 - splay) / 2) # ;)
        self.move(dir, leg_gap)
        self.super_knight(dir)
        self.move(-dir, leg_gap + 2)
        self.travel(dir, leg_gap)

    def use_tower(self, dir):
        self.super_knight(dir)
        self.travel(dir, 1)
        self.move(-dir, 2)
        self.super_knight(dir)
        self.move(-dir, 2)
        self.climb_stairs(-dir, 1)
        self.super_knight(-dir)

    def varcross(self, dir, setting):
        if setting == 1:
            self.super_knight(dir)
        else:
            self.travel(dir, 2)
        self.travel(dir, 1)
        self.crawl_under_table(dir)
        self.travel(dir, 1)
        if setting == 1:
            self.travel(dir, 2)
        else:
            self.super_knight(dir)

    # composite operation
    def crawl_under_table(self, dir, table_width=3, splay=1):
        # inswitch
        self.inswitch(dir, table_width=table_width, splay=splay)
        # cross
        self.travel(dir, max(1, splay - 1))
        # outswitch
        self.outswitch(dir, table_width=table_width, splay=splay)

    def incross(self, dir):
        self.travel(dir, 2)
        self.inswitch(dir, table_width=17, splay=5)

    def outcross(self, dir):
        self.outswitch(dir, table_width=17, splay=5)
        self.travel(dir, 2)

    def gapcross(self, dir):
        self.super_knight(dir)
        self.super_knight(dir)

    # composite operation to cross a climbing tower
    def towercross(self, dir):
        self.incross(dir)
        self.gapcross(dir)
        self.outcross(dir)

########################################################################################

    # UPDATE - support gameplay
    def update(self, force):
        if force == ZERO:  # we are changing grip
            target = self.grid[_(self.player + self.facing)] # index of target block
            if self.grip == ZERO: # we are trying to grab something
                if target in JUGS:
                    self.grip = self.hysteresis
            else: # we are just releasing a slab
                self.grip = ZERO
        elif self.grip:  # we are trying to move a slab
            if force[X]:  # we can ignore attempts to move up or down with a slab
                # we need solid ground to move onto, and can't back into a wall
                if (self.grid[_(self.player + force + DOWN)] != AIR and not
                    (self.grip == -force and self.grid[_(self.player + force)] != AIR)):
                    
                    moved = False
                    fell = False
                    # try to move a slab
                    target = self.grid[_(self.player + self.grip)]
                    if target == ROCKPOINT: # 1x1 slab movement logic
                        pass
                    elif target == ROCKBOTTOM: # vertical slab movement logic
                        top = target + UP
                        while (self.grid[_(top)] == ROCKCOLUMN):
                            top += UP
                        slab = np.ix_(target[X], np.arange(target[Y], top[Y] + 1))
                        dest = slab + force
                        if all(self.grid[dest] == AIR):
                            moved = True
                            self.grid[dest] = self.grid[slab]
                            self.grid[slab] = [AIR]

                            # now, find out how far the slab has to fall
                            airgap = 0
                            while (self.grid[_(dest[0] + DOWN * (1 + airgap))] == AIR):
                                airgap += 1
                            if airgap > 0:
                                fell = True
                                cp = np.copy(self.grid[dest])
                                self.grid[dest] = [AIR]
                                self.grid[dest + DOWN * airgap] = cp
                    else: # horizontal slab movement logic
                        far = target + self.grip
                        while (self.grid[_(far)] == ROCKROW):
                            far += self.grip
                        if self.grid[_(far + self.grip)] == AIR:
                            moved = True
                            cp = np.copy()

                    if moved: # the slab was able to move, so the player should as well
                        self.player += force

                        # end the game if a slab has fallen on the player
                        if self.grid[_(self.player)] in ROCKS:
                            self.complete = True

                        # end the game if all slabs are on the ground
                        if self.unsettled_slabs == 0:
                            self.complete = True

                        if fell:  # our grip has been broken
                            self.grip = ZERO


        else:  # we are just trying to move
            if force == DOWN:
                self.player_fall()
            if force == UP:
                self.jump()
            if force.x:
                self.walk(force)

    def player_fall(self):
        while self.grid[_(self.player + DOWN)] == AIR:
            self.player += DOWN

    def jump(self):
        # no double jumps ):
        if self.grid[_(self.player + DOWN)] != AIR:
            delta_feet = 0
            vertical = 3
            # stop when we hit a ceiling or max jump height
            while self.grid[_(self.player + UP)] == AIR and delta_feet < vertical:
                self.player += UP
                delta_feet += 1
            self.hover = 2

    # move left or right unless blocked by a slab or level edge
    def walk(self, force):
        self.hysteresis = force
        if self.grid[_(self.player + force)] == AIR:
            self.player += force
            self.hover -= 1
            if self.hover <= 0:
                self.player_fall()
                self.hover = 0




