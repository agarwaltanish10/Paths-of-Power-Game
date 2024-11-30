import pygame 
import config
import random, os
from time import sleep

class Rain(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('../graphics/rain.png').convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.75)
        # self.image = random.choice(self.drops)
        self.rect = self.image.get_rect()

        self.vel = pygame.math.Vector2(random.randint(50,100), random.randint(100,200))
        self.rect.x = random.randint(-100, config.P1_SCREEN_WIDTH - 100)
        self.rect.y = random.randint(-config.SCREEN_HEIGHT, -5)

    # def import_assets(self, path):
    #     assets_array = []
    #     for img_file_name in os.listdir(path):
    #         curr_path = path + f'/{img_file_name}'
    #         img_surf = pygame.image.load(curr_path).convert_alpha()
    #         assets_array.append(img_surf)
            
    #     return assets_array

    def update(self, dt):
        if self.rect.bottom > config.SCREEN_HEIGHT+100:
            self.kill()

        self.rect.x += self.vel[0] * dt
        self.rect.y += self.vel[1] * dt
        
class Timer:
    def __init__(self, duration, function):
        self.duration = duration
        self.function = function
        self.is_active = False
        self.start_time = 0

    def activate_timer(self):
        self.start_time = pygame.time.get_ticks()
        self.is_active = True

    def deactivate_timer(self):
        self.start_time = 0
        self.is_active = False

    def update_status_timer(self):
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            if self.function and self.start_time != 0:
                self.function()
            self.deactivate_timer()

class ToolDisplay:
    def __init__(self, p, p1_surf):
        self.p1_surf = p1_surf
        self.player = p

        self.tool_surf = {'bucket': pygame.image.load('../graphics/tools/bucket/bucket.png').convert_alpha(),
                          'basket': pygame.image.load('../graphics/tools/basket/basket.png').convert_alpha()}
        
        self.tool_surf['bucket'] = pygame.transform.scale_by(self.tool_surf['bucket'], 0.4)
        self.tool_surf['basket'] = pygame.transform.scale_by(self.tool_surf['basket'], 0.4)
        
    def disp(self):
        selected_tool_surf = self.tool_surf[self.player.selected_tool]
        selected_tool_rect = selected_tool_surf.get_rect(bottomleft = (0, config.P1_SCREEN_HEIGHT ))
        self.p1_surf.blit(selected_tool_surf, selected_tool_rect)

