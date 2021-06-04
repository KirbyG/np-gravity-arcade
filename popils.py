import pygame
import argparse

from popils_constants import *

# read in 3SAT problem
parser = argparse.ArgumentParser()
input = parser.add_mutually_exclusive_group()
input.add_argument('-i', '--instance', nargs='+', type=str,
                   help="3SAT instance: (default = " + DEFAULT_3SAT + ")")
input.add_argument('-f', '--filename',
                   help="file containing an instance of 3SAT")
args = parser.parse_args()

# Currently these all just blindly accept the input they're given
# TODO Could make input more robust against typos
if args.instance:
    three_sat = " ".join(args.instance)
elif args.filename:
    with open(args.filename) as file:
        three_sat = file.readline()
else:
    three_sat = DEFAULT_3SAT

# initialize all pygame submodules
pygame.init()

# window title
pygame.display.set_caption('Test')

clock = pygame.time.Clock()
window_size = [WINDOW_WIDTH, WINDOW_HEIGHT]
block_size = 50  # block size = 50px TODO dynamic block sizing
# initialize drawing surface
screen = pygame.display.set_mode(window_size)


def place_sub_gadget(code, bottom_row, col):
    for i in range(GADGET_HEIGHT):
        state[bottom_row + i][col] = SUB_GADGETS[code + 1][i]


# TODO 3sat to game state conversion function
def place_gadget(variable_states, bottom_row):
    state[bottom_row][cols - 2] = LADDER
    state[bottom_row + 1][cols - 2] = SUPPORT
    state[bottom_row + 3][cols - 2] = LADDER
    state[bottom_row + 4][cols - 2] = LADDER
    state[bottom_row + 5][cols - 2] = LADDER
    for i in range(2, cols - 2, 2):
        state[bottom_row + 1][i] = SUPPORT
        state[bottom_row + 3][i] = SUPPORT
        state[bottom_row + 4][i] = SUPPORT
    for i in range(len(variable_states)):
        place_sub_gadget(variable_states[i], bottom_row + 1, 2 * i + 1)


# set player position
hidden = SUPPORT

# TODO multiple 3sat instances stored in files
array_form = [int(el) for el in str.split(three_sat)]

row_pointer = 3
tuples = int(len(array_form) / 3)
num_vars = max([abs(el) for el in array_form])
# setup
rows = 6 * (tuples + 1)
cols = 3 + 2 * num_vars
BLOCK = min(window_size[1] / rows, window_size[0] / cols)
state = [[HARD for col in range(cols)] for row in range(rows)]

# bottom 3 rows
redRow = 1
redCol = 1
state[1][1] = PLAYER
for i in range(2, cols - 2):
    state[1][i] = SUPPORT
state[1][cols - 2] = LADDER
for i in range(1, cols - 3, 2):
    state[2][i] = SOFT
state[2][cols - 2] = LADDER
# top 3 rows
state[rows - 2][cols - 2] = PRINCESS
state[rows - 3][cols - 2] = SOFT
# gadgets
print(array_form)
for i in range(tuples):
    index = 3 * i
    variable_states = [UNUSED for k in range(num_vars)]
    for j in range(3):
        temp = array_form[index + j]
        variable_states[abs(temp) - 1] = int(abs(temp) / temp)
    place_gadget(variable_states, row_pointer)
    row_pointer = row_pointer + 6

# setup
done = False
while done is False:  # TODO block breaking logic
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP:  # TODO functions!
            if event.key == pygame.K_LEFT and state[redRow][redCol - 1] != HARD:
                state[redRow][redCol] = hidden
                redCol = redCol - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = PLAYER
            elif event.key == pygame.K_RIGHT and state[redRow][redCol + 1] != HARD:
                state[redRow][redCol] = hidden
                redCol = redCol + 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = PLAYER
            elif event.key == pygame.K_UP:
                if state[redRow + 1][redCol] == SUPPORT or state[redRow + 1][redCol] == LADDER and hidden == LADDER:
                    state[redRow][redCol] = hidden
                    redRow = redRow + 1
                    hidden = state[redRow][redCol]
                    state[redRow][redCol] = PLAYER
                elif state[redRow + 1][redCol] == SOFT:
                    for falling_row in range(redRow + 1, rows - 1):
                        state[falling_row][redCol] = state[falling_row + 1][redCol]
                    state[rows - 1][redCol] = HARD
            elif event.key == pygame.K_DOWN and state[redRow - 1][redCol] != HARD:
                state[redRow][redCol] = hidden
                redRow = redRow - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = PLAYER
        while (state[redRow - 1][redCol] == SUPPORT and hidden == SUPPORT):
            state[redRow][redCol] = hidden
            redRow = redRow - 1
            hidden = state[redRow][redCol]
            state[redRow][redCol] = PLAYER
    screen.fill(BACKGROUND)
    # render
    for row in range(rows):
        for col in range(cols):
            pygame.draw.rect(screen, state[rows - row - 1][col],
                             [col * BLOCK + 1, row * BLOCK + 1, BLOCK - 1, BLOCK - 1])
    pygame.display.flip()
    clock.tick(20)
pygame.quit()
