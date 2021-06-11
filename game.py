class Game:  # tile-based game, either popils or megalit
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.num_rows = 6 * (puzzle.num_clauses + 1)
        self.num_cols = 3 + (2 * puzzle.num_unique_vars)


# If player walks off the top of a ladder, make them fall
        # while (state[player.row - 1][player.col] == SUPPORT and player.occupying == SUPPORT):
        #     game.force(DOWN, player)

# TODO make abstract here, implement in Popils/Megalit
# Change player's coordinates and refresh the displayed game grid
# def move(vector, player):
#     vertical = 0
#     horizontal = 1

#     state[player.row][player.col] = player.occupying
#     player.row += vector[vertical]
#     player.col += vector[horizontal]
#     player.occupying = state[player.row][player.col]
#     state[player.row][player.col] = PLAYER
#     draw(min(player.row, player.row - vector[vertical]), max(player.row, player.row - vector[vertical]),
#          min(player.col, player.col - vector[horizontal]), max(player.col, player.col - vector[horizontal]))


# # Wrapper for move() that enables auto-solving
# def force(vector, player):
#     global state
#     vertical = 0
#     horizontal = 1
#     target = state[player.row + vector[vertical]
#                    ][player.col + vector[horizontal]]

#     if vector == UP:
#         if target == SOFT:
#             for falling_row in range(player.row + 1, ROWS - 1):
#                 state[falling_row][player.col] = state[falling_row + 1][player.col]
#             state[ROWS - 1][player.col] = HARD
#             draw(player.row + 1, ROWS - 1, player.row, player.col)
#         elif player.occupying == LADDER and (target != HARD):
#             move(UP, player)
#     elif target != HARD:
#         move(vector, player)
