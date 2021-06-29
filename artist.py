import pygame
import os
from common_constants import Vector

# in charge of drawing Game objects
class Artist:
    def __init__(self, game):
        self.game = game

        # pygame setup
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
        pygame.init()
        pygame.display.set_caption(f'{type(game).__name__} Reduction')

        # compute constants

        # this is the approximate height of the menu bar at the top of iOS
        BUFFER = 28

        # how much display space we have to work with
        SCREEN_DIM = Vector(pygame.display.Info().current_w - BUFFER, pygame.display.Info().current_h - BUFFER)

        # 
        FITTED_BLOCK_DIM = SCREEN_DIM / game.grid.dim
        MIN_BLOCK_DIM = 15
        self.BLOCK_DIM = max(MIN_BLOCK_DIM, min(FITTED_BLOCK_DIM()))
        self.WINDOW_DIM = Vector(int(round(min(SCREEN_DIM.x - (SCREEN_DIM.x % self.BLOCK_DIM), self.BLOCK_DIM * game.grid.dim.x))), int(round(min(SCREEN_DIM.y - (SCREEN_DIM.y % self.BLOCK_DIM), self.BLOCK_DIM * game.grid.dim.y))))
        self.WINDOW_BLOCKS = Vector(int(round(self.WINDOW_DIM.x / self.BLOCK_DIM)), int(round(self.WINDOW_DIM.y / self.BLOCK_DIM)))
        self.CENTER = Vector(int(self.WINDOW_BLOCKS.x / 2), int(self.WINDOW_BLOCKS.y / 2))

        # store pygame resources
        self.screen = pygame.display.set_mode(self.WINDOW_DIM())
        self.clock = pygame.time.Clock()

        # initial render
        self.draw()

    def grid_to_px(self, x, y, offset):
        return [(x - offset.x) * self.BLOCK_DIM + 1, (self.WINDOW_BLOCKS.y - 1 - (y - offset.y)) * self.BLOCK_DIM + 1, self.BLOCK_DIM - 1, self.BLOCK_DIM - 1]

    def draw(self):
        # compute the offset vector
        offset = Vector(min(self.game.grid.dim.x - self.WINDOW_BLOCKS.x, max(0, self.game.player.pos.x - self.CENTER.x)), min(self.game.grid.dim.y - self.WINDOW_BLOCKS.y, max(0, self.game.player.pos.y - self.CENTER.y)))
        
        # set the background to black
        pygame.draw.rect(self.screen, (0, 0 ,0), [0, 0, self.WINDOW_DIM.x, self.WINDOW_DIM.y])
        
        # draw the subgrid
        for x in range(offset.x, offset.x + self.WINDOW_BLOCKS.x):
            for y in range(offset.y, offset.y + self.WINDOW_BLOCKS.y):
                pygame.draw.rect(self.screen, self.game.grid[x, y].color, self.grid_to_px(x, y, offset))

        # draw player
        pygame.draw.rect(self.screen, self.game.player.color, self.grid_to_px(self.game.player.pos.x, self.game.player.pos.y, offset))

        # display the result
        pygame.display.update()