from game import Game


class Popils(Game):
    pass

    def initSpecialAreas():
        player_row = player_col = 1
        assignment_row = 2
        transition_col = COLS - 2  # Column with path (ladders) between areas
        # Initially set entire zone to indestructible blocks
        # Using this "*" notation twice doesn't produce expected results
        #   because Python just makes pointers to original tuple
        block_type = [[HARD] * COLS for row in range(ROWS)]

        # Starting zone
        block_type[player_row][player_col] = PLAYER
        for i in range(player_col + 1, transition_col):
            block_type[player_row][i] = SUPPORT
        block_type[player_row][transition_col] = LADDER
        for i in range(player_col, transition_col - 1, 2):
            block_type[assignment_row][i] = SOFT
        block_type[assignment_row][transition_col] = LADDER

        # Ending zone
        block_type[ROWS - 2][transition_col] = PRINCESS
        # Stop princess from walking
        block_type[ROWS - 3][transition_col] = SOFT

        # Send back partially-built level
        return block_type

    def initSatisfiabilityClauses():
        row_pointer = 3

        for tuple in range(NUM_TUPLES):
            index = VARS_PER_TUPLE * tuple
            variable_states = [ABSENT] * NUM_VARS

            # Determine which variables were used in which clauses
            for offset in range(VARS_PER_TUPLE):
                var = array_form[index + offset]
                # Convert variable label --> variable state
                variable_states[abs(var) - 1] = sign(var)
            # Fill in gadget region for each variable for current tuple
            place_gadget(variable_states, row_pointer)
            row_pointer += GADGET_HEIGHT

    def place_gadget(variable_states, bottom_row):
        start_col = 2
        transition_col = COLS - 2  # Column with path (ladders) between areas

        # Create transition to next zone
        state[bottom_row][transition_col] = LADDER
        state[bottom_row + 1][transition_col] = SUPPORT
        # state[bottom_row + 2][transition_col] is already HARD
        state[bottom_row + 3][transition_col] = LADDER
        state[bottom_row + 4][transition_col] = LADDER
        state[bottom_row + 5][transition_col] = LADDER

        # Carve out walkable area, skipping gadget columns
        for i in range(start_col, transition_col, 2):
            state[bottom_row + 1][i] = SUPPORT
            state[bottom_row + 3][i] = SUPPORT
            state[bottom_row + 4][i] = SUPPORT

        # Place ladders according to gadget structure
        for var_index in range(len(variable_states)):
            place_sub_gadget(
                variable_states[var_index], bottom_row + 1, 2 * var_index + 1)

    # Clone sub-gadget ladder structure

    def place_sub_gadget(var_state, bottom_row, col):
        for i in range(SUB_GADGET_HEIGHT):
            state[bottom_row + i][col] = SUB_GADGETS[var_state + 1][i]


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
