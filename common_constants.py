# Definition of 3SAT
VARS_PER_CLAUSE = 3

# colors named based on in-game functionality
COLORS = {
    'ladder': (0, 0, 255),
    'hard': (210, 180, 140),
    'breakable': (128, 128, 128),
    'princess': (250, 20, 200),
    'support': (255, 255, 255),
    'air': (255, 255, 255),
    'slab': (128, 128, 128),
    'border': (0, 200, 0),
    'tip':  (110,  110, 110),
    'gripped': (50, 50, 50),
    'background': (0, 0, 0)
}


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        from math import sqrt
        self.magnitude = sqrt(self.x * self.x + self.y * self.y)

    def __matmul__(self, other):
        return self.x * other.x + self.y * other.y

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

    # the zero vector is false, all others are true
    def __bool__(self):
        return self.magnitude != 0.0

    def __truediv__(self, other):
        return Vector(self.x / other.x, self.y / other.y)


LEFT = Vector(-1, 0)
RIGHT = Vector(1, 0)
UP = Vector(0, 1)
DOWN = Vector(0, -1)
ZERO = Vector(0, 0)
