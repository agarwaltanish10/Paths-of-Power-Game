import pygame 
import config
import random, os
from time import sleep

class Rain(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('../graphics/rain.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.75)
        self.rect = self.image.get_rect()

        self.vel = pygame.math.Vector2(random.randint(50,100), random.randint(100,200))
        self.rect.x = random.randint(-100, config.P1_SCREEN_WIDTH - 100)
        self.rect.y = random.randint(-config.SCREEN_HEIGHT, -5)

    def update(self, dt):
        if self.rect.bottom > config.SCREEN_HEIGHT+100:
            self.kill()

        self.rect.x += self.vel[0] * dt
        self.rect.y += self.vel[1] * dt
        
