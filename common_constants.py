# Definition of 3SAT
VARS_PER_CLAUSE = 3

# common vectors
ZERO = [0, 0]
LEFT = [0, -1]
RIGHT = [0, 1]
UP = [1, 0]
DOWN = [-1, 0]

# colors named based on in-game functionality
COLORS = {
          'ladder': (0, 0, 255),
          'hard': (210, 180, 140),
          'soft': (128, 128, 128),
          'princess': (250, 20, 200),
          'support': (255, 255, 255),
          'air': (255, 255, 255),
          'slab': (128, 128, 128),
          'border': (0, 0, 0),
          'tip':  (110,  110, 110),
          'gripped': (50, 50, 50)
        }

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        from math import sqrt
        self.magnitude = sqrt(self.x * self.x + self.y * self.y)

    def __matmul__(self, other):
        return Vector(self.x * other.x, self.y * other.y)

    # pure function
    def normalize(self):
        return Vector(self.x / self.magnitude, self.y / self.magnitude)

    def __rmul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
          self.x += other.x
          self.y += other.y
          return self

    def __eq__(self, other):
          return self.x == other.x and self.y == other.y

    # aliasing for convenient matrix access use cases
    def __getattr__(self, name):
        if name == 'row':
            return self.y
        if name == 'col':
            return self.x
        raise AttributeError

    # for ease of splitting into components when needed
    def __call__(self):
        return self.x, self.y
    
    def __repr__(self):
        return '{}, {}'.format(self.x, self.y)

# wrapper for a 2d matrix allowing vector indexing
class Grid:
    def __init__(self, *args):
        if type(args[-1]) == type(lambda: None):
            initializer = args[-1]
            args = args[:-1]
        else:
            initializer = lambda: None
        if len(args) == 1:
            size = args[0]
        else:
            size = Vector(args[1], args[0])
        self.grid = [[initializer() for col in range(size.col)] for row in range(size.col)]
        
    def __getitem__(self, key):
        if type(key) == Vector:
            return self.grid[int(key.row)][int(key.col)]
        else:
            return self.grid[key]
    
    def __setitem__(self, key, value):
        if type(key) == Vector:
            self.grid[int(key.row)][int(key.col)] = value
        else:
            self.grid[key] = value

left = Vector(LEFT[1],  LEFT[0])
right = Vector(RIGHT[1], RIGHT[0])
up = Vector(UP[1], UP[0])
down = Vector(DOWN[1], DOWN[0])
zero = Vector(ZERO[1], ZERO[0])