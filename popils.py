#TODO refactor kirby's bad code
import sys
#sys.path.append('/Users/kirby/anaconda3/lib/python3.7/site-packages/')
import pygame
import random
pygame.init()
size = [801, 601]
ROW = 1
COL = 0
BLOCK = 50 #block size = 50px TODO dynamic block sizing
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Test')
player = (255, 0, 0) #red
ladder = (0, 0, 255) #blue
hard = (210, 180, 140) #tan
soft = (128, 128, 128) #gray
princess = (250, 20, 150) #pink
support = (255, 255, 255) #white
background = (0, 0, 0) #black
clock = pygame.time.Clock()
done = False
###setup
rows = int(size[ROW] / BLOCK)
cols = int(size[COL] / BLOCK)
colors = [player, ladder, hard, soft, princess, support]
#state = [[colors[random.randint(0, 5)] for col in range(cols)] for row in  range(rows)]
state = [[support for col in range(cols)] for row in  range(rows)]
state[0] = [hard for col in range(cols)]
state[rows - 1] = [hard for col in range(cols)]
state[rows - 2][1] = player
state[rows - 3][1] = soft
state[rows - 3][2] = hard
state[rows - 3][3] = soft
state[rows - 3][4] = hard
state[rows - 3][5] = soft
state[rows - 3][6] = hard
state[rows - 3][7] = soft
state[rows - 3][8] = hard
state[rows - 3][9] = soft
state[rows - 3][10] = hard
state[rows - 3][11] = soft
state[rows - 3][12] = hard
state[rows - 3][13] = soft
state[rows - 2][14] = ladder
state[rows - 3][14] = ladder
state[rows - 4][14] = ladder
state[rows - 5][14] = ladder
state[rows - 6][14] = princess
state[rows - 4][13] = hard
state[rows - 4][12] = hard
state[rows - 4][11] = ladder
state[rows - 4][10] = ladder


def place_gadget(variable_states, coords): #TODO 3sat to game state conversion function
    pass
for row in range(rows):
    state[row][0] = hard
    state[row][cols - 1] = hard
#set player position
redRow = rows - 2
redCol = 1
hidden = support
#TODO multiple 3sat instances stored in files
#get 3sat input or use default
three_sat = input('enter 3sat instance in the format: -3 -2 4 2 7 -4, or enter a filename:')
test_input = '!3 !2 4 2 7 !4'
print(str.split(test_input))

test_input = '-3 -2 4 2 7 -4'
array_form = str.split(test_input)
from enum import Enum
class state (Enum):
    UNUSED = 0
    NEGATED = -1
    NONNEGATED = 1
coords = [0, 0]
for i in range(len(array_form) / 3):
    index = 3 * i
    variable_states = [state.UNUSED for i in range(max(abs(array_form)))]
    for j in range(3):
        temp = array_form[i + j]
        variable_states[abs(temp) - 1] = abs(temp) / temp
    place_gadget(variable_states, coords)
    coords[1] = coords[1] + 6
    
    
###setup
while (done == False): #TODO block breaking logic
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP: #TODO functions!
            if event.key == pygame.K_LEFT and state[redRow][redCol - 1] != hard:
                state[redRow][redCol] = hidden
                redCol = redCol - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = player
            elif event.key == pygame.K_RIGHT and state[redRow][redCol + 1] != hard:
                state[redRow][redCol] = hidden
                redCol = redCol + 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = player
            elif event.key == pygame.K_UP and state[redRow - 1][redCol] != hard and hidden == ladder:
                state[redRow][redCol] = hidden
                redRow = redRow - 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = player
            elif event.key == pygame.K_DOWN and state[redRow + 1][redCol] != hard:
                state[redRow][redCol] = hidden
                redRow = redRow + 1
                hidden = state[redRow][redCol]
                state[redRow][redCol] = player
        while (state[redRow + 1][redCol] == support):
            state[redRow][redCol] = hidden
            redRow = redRow + 1
            hidden = state[redRow][redCol]
            state[redRow][redCol] = player
    screen.fill(background)
    #render
    for row in range(rows):
        for col in  range(cols):
            pygame.draw.rect(screen, state[row][col], [col * BLOCK + 1, row * BLOCK + 1, BLOCK - 1, BLOCK - 1])
    #render
    pygame.display.flip()
    clock.tick(20);
pygame.quit()
