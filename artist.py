import pygame
from common import LEFT, RIGHT, UP, DOWN, ZERO
from common import X, Y
from common import COLORS, AIR, PLAYER
import numpy as np

v_min = np.vectorize(min)
v_max = np.vectorize(max)
v_int = np.vectorize(int)

# in charge of drawing Game objects
class Artist:
    def __init__(self, game):
        self.game = game

        # pygame setup
        pygame.init()
        pygame.display.set_caption(f'{type(game).__name__} Reduction')

        # compute constants

        # this is the approximate height of the menu bar at the top of MacOS
        BUFFER_PX = 280

        # how much display space we have to work with
        SCREEN_PX = np.array([
            pygame.display.Info().current_w,
            pygame.display.Info().current_h
        ]) - BUFFER_PX

        # blocks are at least 15px, but can be larger when the grid is small
        self.BLOCK_PX = max(15, int(np.min(SCREEN_PX / game.grid.shape)))

        # limit the max window dimension to fit on the display, and ensure it multiplies the block dimension
        self.WINDOW_PX = v_min(
            SCREEN_PX - (SCREEN_PX % self.BLOCK_PX),
            self.BLOCK_PX * np.array(game.grid.shape)
        )

        # the number of blocks that will fit in a window at a time
        self.VIEWPORT_SHAPE = v_int(self.WINDOW_PX / self.BLOCK_PX)

        # position of the player on the screen while scrolling is active
        self.CENTER = v_int(self.VIEWPORT_SHAPE / 2)

        # store pygame resources
        self.screen = pygame.display.set_mode(self.WINDOW_PX)
        self.clock = pygame.time.Clock()

        # initial render
        self.draw()

    # all params are in block units
    # Note: the y coordinate is inverted because pygame considers the upper
    # left corner of the window to be the origin, while all logical objects
    # rely on a more standard coordinate system originating in the lower left
    def grid_to_px(self, x, y, offset):
        corner_x = (x - offset[X]) * self.BLOCK_PX + 1
        corner_y = (self.VIEWPORT_SHAPE[Y] - 1 - (y - offset[Y])) * self.BLOCK_PX + 1
        return [corner_x, corner_y, self.BLOCK_PX, self.BLOCK_PX]

    def shrink(self, rect, short_sides):
        reduction = 1

        if short_sides:
            rect[0] += (reduction if short_sides.count(LEFT) else 0)
            rect[1] += (reduction if short_sides.count(UP) else 0)
            rect[2] -= reduction * \
                (short_sides.count(LEFT) + short_sides.count(RIGHT))
            rect[3] -= reduction * \
                (short_sides.count(DOWN) + short_sides.count(UP))
        return rect

    def draw(self):
        # compute the offset vector
        offset = v_min(
            self.game.grid.shape - self.VIEWPORT_SHAPE,
            v_max(ZERO, self.game.player - self.CENTER)
        )

        # set the background to white
        pygame.draw.rect(
            self.screen,
            COLORS[AIR],
            [0, 0, self.WINDOW_PX[X], self.WINDOW_PX[Y]])

        # draw the subgrid
        for x in range(offset[X], offset[X] + self.VIEWPORT_SHAPE[X]):
            for y in range(offset[Y], offset[Y] + self.VIEWPORT_SHAPE[Y]):
                pygame.draw.rect(
                    self.screen,
                    COLORS[self.game.grid[x, y]],
                    self.grid_to_px(x, y, offset)
                )

        # draw player
        pygame.draw.rect(
            self.screen,
            COLORS[PLAYER],
            self.grid_to_px(self.game.player[X], self.game.player[Y], offset))

        # display the result
        pygame.display.update()
