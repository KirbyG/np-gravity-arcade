import builtins
from game import Game, Block, Player
from common_constants import LEFT, RIGHT, UP, DOWN, ZERO, left, right, up, down, zero, Vector, Grid
from math import sqrt



# Megalit was developed by the ASCII Corporation for the Gameboy
class Megalit(Game):
    def __init__(self, puzzle):
        super().__init__(puzzle)

    def solve(self, puzzle):
        return [UP]

    def build_slab(self, grid, origin, extent):
        step = extent.normalize()
        grid[origin] = Block('tip', connections=[step])
        for offset in range(1, int(extent.magnitude) - 1):
            position = origin + (offset * step)
            grid[position] = Block('slab', connections=[step, -1 * step])
        end = origin + ((extent.magnitude - 1) * step)
        grid[end] = Block('tip', connections=[-1 * step])

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
        self.build_slab(grid, Vector(4, 1), Vector(2, 0))
        self.build_slab(grid, Vector(6, 1), Vector(0, 2))
        self.build_slab(grid, Vector(8, 1), Vector(0, 2))
        self.build_slab(grid, Vector(5, 3), Vector(3, 0))
        self.build_slab(grid, Vector(6, 4), Vector(0, 2))
        self.build_slab(grid, Vector(5, 6), Vector(3, 0))
        self.player = Player([1, 1])
        return grid

    # returns a list of vectors
    def reconstruct_slab(self, tip):
        if self.grid[tip].type == 'air':
            return None
        slab = [tip]
        prop_dir = self.grid[tip].connections[0]
        while self.grid[slab[-1] + prop_dir].type != 'tip':
            slab.append(slab[-1] + prop_dir)
        return slab

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
    def slab_fall(self, slab):
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

    def push(self, force):
        slab = self.reconstruct_slab(self.player.pos)
        self.slab_fall(slab)
        if self.grid[self.player.pos].type in ('slab', 'tip'):
            self.complete = True
    
    def player_fall(self):
        while self.grid[self.player.pos + down].type == 'air':
            self.player.pos += down

    def update(self, vector):
        print('updating')
        force = Vector(vector[1], vector[0])
        pos: Vector = self.player.pos
        
        if force.magnitude == 0:
            print('grip command')
            if self.grid[pos + left].type == 'tip':
                self.grid[pos + left].type = 'gripped'
                self.player.gripping = left
            elif self.grid[pos + left].type == 'gripped':
                self.grid[pos + left].type = zero
            elif self.grid[pos + right].type == 'tip':
                self.grid[pos + right].type = 'gripped'
                self.player.gripping = right
            elif self.grid[pos + right].type == 'gripped':
                self.grid[pos + right].type = 'tip'
                self.player.gripping = zero
        else:
            if force == down and self.grid[pos + down].type == 'air':
                self.player_fall()
            if force == up and self.grid[pos + down].type != 'air':
                count = 0
                while self.grid[pos + up].type == 'air' and count < 3:
                    pos += up
                    count += 1
            if force == left or force == right:
                antiforce = -1 * force
                if self.player.gripping == force:
                    pos += force
                    self.push(force)
                elif self.player.gripping == antiforce:
                    if self.grid[pos + force + down].type == 'air':
                        self.player.gripping = zero
                        pos += force
                        self.player_fall()
                    else:
                        self.push(force)
                        pos += force
                else:
                    if self.grid[pos + force].type == 'air':
                        pos += force
                    self.player_fall()
                        
        self.altered_rows = [0, self.num_rows - 1]
        self.altered_cols = [0, self.num_cols - 1]