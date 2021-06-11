

# ----- Function definitions -----


# Change player's coordinates and refresh the displayed game grid
def move(vector, player):
    vertical = 0
    horizontal = 1

    state[player.row][player.col] = player.occupying
    player.row += vector[vertical]
    player.col += vector[horizontal]
    player.occupying = state[player.row][player.col]
    state[player.row][player.col] = PLAYER
    draw(min(player.row, player.row - vector[vertical]), max(player.row, player.row - vector[vertical]),
         min(player.col, player.col - vector[horizontal]), max(player.col, player.col - vector[horizontal]))


# Wrapper for move() that enables auto-solving
def force(vector, player):
    global state
    vertical = 0
    horizontal = 1
    target = state[player.row + vector[vertical]
                   ][player.col + vector[horizontal]]

    if vector == UP:
        if target == SOFT:
            for falling_row in range(player.row + 1, ROWS - 1):
                state[falling_row][player.col] = state[falling_row + 1][player.col]
            state[ROWS - 1][player.col] = HARD
            draw(player.row + 1, ROWS - 1, player.row, player.col)
        elif player.occupying == LADDER and (target != HARD):
            move(UP, player)
    elif target != HARD:
        move(vector, player)


def generateSolution():
    steps = []
    global nested_form
    else:
        # set variables
        for truthiness in good_guess:
            if truthiness == 1:
                steps.append(UP)
            steps.append(RIGHT)
            steps.append(RIGHT)
        # traverse level
        for tuple in range(NUM_TUPLES):
            steps.append(UP)
            steps.append(UP)
            steps.append(UP)
            lateral_blocks = 2 * (NUM_VARS + 1 - max([abs(nested_form[tuple][var])
                                                      for var in range(VARS_PER_TUPLE) if passes(nested_form[tuple][var], good_guess)]))

            # Move to nearest viable ladder
            for i in range(lateral_blocks):
                steps.append(LEFT)
            steps.append(UP)
            steps.append(UP)
            for i in range(lateral_blocks):
                steps.append(RIGHT)
            steps.append(UP)

        # Climb to princess
        steps.append(UP)
        steps.append(UP)
        steps.append(UP)

        return steps
