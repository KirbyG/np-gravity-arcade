
import sys
import pygame
import random

import popils_constants as const

# initialize all pygame submodules
pygame.init()

# window title
pygame.display.set_caption('Test')

clock = pygame.time.Clock()
size = [801, 601]
block_size = 50  # block size = 50px TODO dynamic block sizing
screen = pygame.display.set_mode(size)
done = False

# setup
rows = int(size[const.ROW] / block_size)
cols = int(size[const.COL] / block_size)
colors = [const.PLAYER, const.LADDER, const.HARD,
          const.SOFT, const.PRINCESS, const.SUPPORT]

#state = [[colors[random.randint(0, 5)] for col in range(cols)] for row in  range(rows)]
state = [[const.SUPPORT for col in range(cols)] for row in range(rows)]
state[0] = [const.HARD for col in range(cols)]
state[rows - 1] = [const.HARD for col in range(cols)]
state[rows - 2][1] = const.PLAYER
state[rows - 3][1] = const.SOFT
state[rows - 3][2] = const.HARD
state[rows - 3][3] = const.SOFT
state[rows - 3][4] = const.HARD
state[rows - 3][5] = const.SOFT
state[rows - 3][6] = const.HARD
state[rows - 3][7] = const.SOFT
state[rows - 3][8] = const.HARD
state[rows - 3][9] = const.SOFT
state[rows - 3][10] = const.HARD
state[rows - 3][11] = const.SOFT
state[rows - 3][12] = const.HARD
state[rows - 3][13] = const.SOFT
state[rows - 2][14] = const.LADDER
state[rows - 3][14] = const.LADDER
state[rows - 4][14] = const.LADDER
state[rows - 5][14] = const.LADDER
state[rows - 6][14] = const.PRINCESS
state[rows - 4][13] = const.HARD
state[rows - 4][12] = const.HARD
state[rows - 4][11] = const.LADDER
state[rows - 4][10] = const.LADDER


def place_gadget(variable_states, coords):  # TODO 3sat to game state conversion function
    pass


for row in range(rows):
    state[row][0] = const.HARD
    state[row][cols - 1] = const.HARD
# set const.PLAYER position
redRow = rows - 2
redCol = 1
hidden = const.SUPPORT
# TODO multiple 3sat instances stored in files
# get 3sat input or use default
three_sat = input(
    'enter 3sat instance in the format: -3 -2 4 2 7 -4, or enter a filename:')
test_input = '!3 !2 4 2 7 !4'
print(str.split(test_input))

test_input = '-3 -2 4 2 7 -4'
array_form = str.split(test_input)


coords = [0, 0]
for i in range(len(array_form) / 3):
    index = 3 * i
    variable_states = [state.UNUSED for i in range(max(abs(array_form)))]
    for j in range(3):
        temp = array_form[i + j]
        variable_states[abs(temp) - 1] = abs(temp) / temp
    place_gadget(variable_states, coords)
    coords[1] = coords[1] + 6


# setup
while (done == False):  # TODO block breaking logic
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP:  # TODO functions!
            if event.key == pygame.K_LEFT and state[redRow][redCol - 1] != const.HARD:
                state[redRow][redCol] = hidden
                redCol = redCol - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = const.PLAYER
            elif event.key == pygame.K_RIGHT and state[redRow][redCol + 1] != const.HARD:
                state[redRow][redCol] = hidden
                redCol = redCol + 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = const.PLAYER
            elif event.key == pygame.K_UP and state[redRow - 1][redCol] != const.HARD and hidden == const.LADDER:
                state[redRow][redCol] = hidden
                redRow = redRow - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = const.PLAYER
            elif event.key == pygame.K_DOWN and state[redRow + 1][redCol] != const.HARD:
                state[redRow][redCol] = hidden
                redRow = redRow + 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = const.PLAYER
        while (state[redRow + 1][redCol] == const.SUPPORT):
            state[redRow][redCol] = hidden
            redRow = redRow + 1
            hidden = state[redRow][redCol]
            state[redRow][redCol] = const.PLAYER
    screen.fill(background)
    # render
    for row in range(rows):
        for col in range(cols):
            pygame.draw.rect(screen, state[row][col], [
                             col * block_size + 1, row * block_size + 1, block_size - 1, block_size - 1])
    # render
    pygame.display.flip()
    clock.tick(20)
pygame.quit()
