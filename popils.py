
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


UNUSED = 0
NEGATED = -1
NONNEGATED = 1
sub_gadgets = [[const.LADDER, const.LADDER, const.SUPPORT, const.LADDER], [const.LADDER, const.SUPPORT, const.LADDER, const.SUPPORT], [const.SUPPORT, const.LADDER, const.LADDER, const.SUPPORT]]
def place_sub_gadget(code, bottom_row, col):
    for i in range(4):
        state[bottom_row + i][col] = sub_gadgets[code + 1][i]
def place_gadget(variable_states, bottom_row): #TODO 3sat to game state conversion function
    state[bottom_row][cols - 2] = const.LADDER
    state[bottom_row + 3][cols - 2] = const.LADDER
    state[bottom_row + 4][cols - 2] = const.LADDER
    state[bottom_row + 5][cols - 2] = const.LADDER
    for i in range(2, cols - 2, 2):
        state[bottom_row + 1][i] = const.SUPPORT
        state[bottom_row + 3][i] = const.SUPPORT
        state[bottom_row + 4][i] = const.SUPPORT
    for i in range(len(variable_states)):
        place_sub_gadget(variable_states[i], bottom_row + 1, 2 * i + 1)
#set player position

hidden = const.SUPPORT
#TODO multiple 3sat instances stored in files
#get 3sat input or use default
three_sat = input('enter 3sat instance in the format: -3 -2 4 2 7 -4, or enter a filename:')
array_form = [int(el) for el in str.split(three_sat)]

row_pointer = 3
tuples = int(len(array_form) / 3)
num_vars = max([abs(el) for el in array_form])
###setup
rows = 6 * (tuples + 1)
cols = 3 + 2 * num_vars
BLOCK = min(size[1] / rows, size[0] / cols)
colors = [const.PLAYER, const.LADDER, const.HARD, const.SOFT, const.PRINCESS, const.SUPPORT]
state = [[const.HARD for col in range(cols)] for row in  range(rows)]

#bottom 3 rows
redRow = 1
redCol = 1
state[1][1] = const.PLAYER
for i in range(2, cols - 2):
    state[1][i] = const.SUPPORT
state[1][cols - 2] = const.LADDER
for i in range(1, cols - 3, 2):
    state[2][i] = const.SOFT
state[2][cols - 2] = const.LADDER
#top 3 rows
state[rows - 2][cols - 2] = const.PRINCESS
state[rows - 3][cols - 2] = const.SOFT
#gadgets
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
                redRow = redRow + 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = const.PLAYER
            elif event.key == pygame.K_DOWN and state[redRow + 1][redCol] != const.HARD:
                state[redRow][redCol] = hidden
                redRow = redRow - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = const.PLAYER
        '''while (state[redRow + 1][redCol] == const.SUPPORT):
            state[redRow][redCol] = hidden
            redRow = redRow + 1
            hidden = state[redRow][redCol]
            state[redRow][redCol] = const.PLAYER
'''
        while (state[redRow + 1][redCol] == const.SUPPORT):
            state[redRow][redCol] = hidden
            redRow = redRow + 1
            hidden = state[redRow][redCol]
            state[redRow][redCol] = const.PLAYER
    screen.fill(const.BACKGROUND)
    # render
    for row in range(rows):
        for col in  range(cols):
            pygame.draw.rect(screen, state[rows - row - 1][col], [col * BLOCK + 1, row * BLOCK + 1, BLOCK - 1, BLOCK - 1])
    pygame.display.flip()
    clock.tick(20)
pygame.quit()
