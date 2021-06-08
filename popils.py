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
    for i in range(SUB_GADGET_HEIGHT):
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
tuples = int(len(array_form) / 3)
nested_form = [[array_form[3 * i + j] for j in range(3)] for i in range(tuples)]

row_pointer = 3

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
def sign(num):
    return int(abs(num) / num)
for i in range(tuples):
    variable_states = [UNUSED for k in range(num_vars)]
    for j in range(3):
        temp = nested_form[i][j]
        variable_states[abs(temp) - 1] = sign(temp)
    place_gadget(variable_states, row_pointer)
    row_pointer = row_pointer + 6

# setup
screen.fill(BACKGROUND)
def draw(min_row, max_row, min_col, max_col):
    global state, screen
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            pygame.draw.rect(screen, state[row][col],
                             [col * BLOCK + 1, (rows - row - 1) * BLOCK + 1, BLOCK - 1, BLOCK - 1])
    pygame.display.update()
draw(0, rows - 1, 0, cols - 1)
def move(vector):
    global state, hidden, redRow, redCol, fresh
    
    if vector == UP and state[redRow + 1][redCol] == SOFT:
        fresh = False
        
    else:
        state[redRow][redCol] = hidden
        redRow = redRow + vector[0]
        redCol = redCol + vector[1]
        hidden = state[redRow][redCol]
        state[redRow][redCol] = PLAYER
        draw(min(redRow, redRow - vector[0]), max(redRow, redRow - vector[0]), 
             min(redCol, redCol - vector[1]), max(redCol, redCol - vector[1]))
def force(vector):
    global state, hidden, redRow, redCol, fresh
    target = state[redRow + vector[0]][redCol + vector[1]]
    if vector == UP:
        if target == SOFT:
            fresh = False
            for falling_row in range(redRow + 1, rows - 1):
                state[falling_row][redCol] = state[falling_row + 1][redCol]
            state[rows - 1][redCol] = HARD
            draw(redRow + 1, rows - 1, redCol, redCol)
        elif hidden == LADDER and (target != HARD):
            move(UP)
    elif target != HARD:
        move(vector)
done = False
fresh = True
solution = []
autosolve = -1
count = 0
def passes(var, guess):
    return sign(var) * guess[abs(var) - 1] == 1
while done is False:
    if autosolve > -1: #TODO why is this slow??
        force(solution[autosolve])
        autosolve = autosolve + 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        else:
            if event.type == pygame.KEYUP:  # TODO functions!
                if event.key == pygame.K_LEFT:
                    force(LEFT)
                elif event.key == pygame.K_RIGHT:
                    force(RIGHT)
                elif event.key == pygame.K_UP:
                    force(UP)
                elif event.key == pygame.K_DOWN and state[redRow - 1][redCol] != HARD:
                    force(DOWN)
        while (state[redRow - 1][redCol] == SUPPORT and hidden == SUPPORT):
            force(DOWN)
    if fresh and redRow == 1 and redCol == 1 and event.type == pygame.KEYUP and event.key == pygame.K_a:
        #autosolve
        autosolve = 0
        #compute vector sequence
        #find the solving variable assignment by brute force
        good_guess = []
        for guess in range(2 ** num_vars):
            form = r'{:0' + str(num_vars) + r'b}'
            parsed_guess = [int(form.format(guess)[j]) * 2 - 1 for j in range(num_vars)]
            solve = True
            for clause in range(tuples):
                satisfied = False
                for var in range(3):
                    temp = nested_form[clause][var]
                    if passes(temp, parsed_guess):
                        satisfied = True
                        parsed_guess
                if satisfied is False:
                    solve = False
                    break
            if solve:
                good_guess = parsed_guess
        if len(good_guess) == 0:
            done = True
        else:
            #set variables
            for var in good_guess:
                if var == 1:
                    solution.append(UP)
                solution.append(RIGHT)
                solution.append(RIGHT)
            #traverse level
            for tuple in range(tuples):
                solution.append(UP)
                solution.append(UP)
                solution.append(UP)
                shuffle = 2 * (11 - max([abs(nested_form[tuple][var]) for var in range(3) if passes(nested_form[tuple][var], good_guess)]))
                for i in range(shuffle):
                    solution.append(LEFT)
                solution.append(UP)
                solution.append(UP)
                for i in range(shuffle):
                    solution.append(RIGHT)
                solution.append(UP)
            solution.append(UP)
            solution.append(UP)
            solution.append(UP)
    print('loop', count)
    count = count + 1
    clock.tick(20)
pygame.quit()
