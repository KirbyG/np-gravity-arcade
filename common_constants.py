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
          'support': (255, 255, 255)
        }