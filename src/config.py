import pygame
from pygame.locals import *

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

P1_SIZE = pygame.math.Vector2()
P2_SIZE = pygame.math.Vector2()

P1_SCREEN_WIDTH = P1_SIZE[0]
P1_SCREEN_HEIGHT = P1_SIZE[1]

P2_SCREEN_WIDTH = P2_SIZE[0]
P2_SCREEN_HEIGHT = P2_SIZE[1]

MAP_SIZE = pygame.math.Vector2()

def game_font(size):
    return pygame.font.Font('../fonts/minecraft.ttf', size)


