import pygame, sys, random
from pygame.locals import K_LEFTBRACKET, K_RIGHTBRACKET, K_TAB
from pytmx.util_pygame import load_pygame
from time import sleep
from player import *
from support import *
import config

class Level:
    def __init__(self, p1_surf, p2_surf):
        self.surf = pygame.display.get_surface()
        self.p1_surf = p1_surf
        self.p2_surf = p2_surf

        self.all_sprites = Camera(p1_surf, p2_surf)
        self.collision_sprites = pygame.sprite.Group()
        self.daynightcycle = DayNightCycle(p1_surf)
        self.minimap = MiniMap(p1_surf)

        self.fruit_sprites = pygame.sprite.Group()
        self.fruit_pos = [(32*59.5, 32*12), (32*59.5, 32*8), (32*59.5, 32*4)]

        self.load_map()
        self.player = Player(self.all_sprites, [640,640], self.collision_sprites, self.fruit_sprites, self.fruit_pos)
        self.tool_display = ToolDisplay(self.player, self.p1_surf)

        self.day_counter = 1
        self.text_displayed = False

        self.is_raining = True
        self.num_raindrops = random.randint(50, 100)
        if self.is_raining:
            for i in range(self.num_raindrops):
                self.rain = Rain()
                self.all_sprites.add(self.rain)
        self.is_raining = False

        # days
        self.dayone = DayOne(self.p1_surf)

                
    def load_map(self):
        tiled_map = load_pygame('../tsx/untitled.tmx')
        
        fruits = [None] * 3
        for i in range(len(fruits)):
            fruits[i] = Fruit([self.all_sprites, self.fruit_sprites], self.fruit_pos[i], self.fruit_sprites)

        fence_tiles = tiled_map.get_layer_by_name('fence').tiles()
        for x,y,tile_surface in fence_tiles:
            position = (32*x, 32*y)
            Fence(tile_surface, [self.all_sprites, self.collision_sprites], position)

        collision_tiles = tiled_map.get_layer_by_name('collision').tiles()
        for x,y,_ in collision_tiles:
            position = (32*x, 32*y)
            tile_surface = pygame.Surface((32, 32))
            tile_surface_w = tile_surface.get_size()[0]
            tile_surface_h = tile_surface.get_size()[1]
            MapObject(tile_surface, self.collision_sprites, position, tile_surface_w, tile_surface_h, 0, 0)

        # objects - trees, well etc
        objects_layer = tiled_map.get_layer_by_name('objects')
        for obj in objects_layer:
            position = (obj.x, obj.y)
            if obj.name != 'tree':
                MapObject(obj.image, [self.all_sprites, self.collision_sprites],
                    position, obj.width, obj.height)
            else:
                Tree(obj.image, [self.all_sprites, self.collision_sprites],
                    position, obj.width, obj.height)
                
    def run_level_day(self, dt):
        self.all_sprites.display_sprites(self.player)
        sprite_pos = self.player.update(dt)
        self.all_sprites.update(dt)

        self.tool_display.disp()

        self.daynightcycle.cycle(dt)
        self.minimap.render_minimap(sprite_pos)

    def run_level(self, dt):

        self.run_level_day(dt)

        if self.day_counter == 1:
            self.start_time = pygame.time.get_ticks()
            self.dayone.run_day()
            self.day_counter = 50

        if pygame.time.get_ticks() - self.start_time > 8000 and not self.text_displayed:
            self.dayone.typewriter_effect(self.p1_surf)
            self.text_displayed = True
            
    
class Camera(pygame.sprite.Group):
    def __init__(self, p1_surf, p2_surf):
        super().__init__()
        self.surf = pygame.display.get_surface()
        self.p1_surf = p1_surf
        self.p2_surf = p2_surf

        # including the camera offset for following the player
        self.offset = pygame.math.Vector2()
        self.half_p1_width = config.P1_SCREEN_WIDTH // 2
        self.half_p1_height = config.P1_SCREEN_HEIGHT // 2

        # ground map
        self.map_surf = pygame.image.load('../graphics/village_map.png').convert_alpha()
        self.map_rect = self.map_surf.get_rect(topleft = (0,0))
        config.MAP_SIZE = self.map_surf.get_size()

        # zoom settings
        self.was_pressed = K_TAB
        self.zoom = 1
        self.temp_size = (2500,2500)
        self.aux_surf = pygame.Surface(self.temp_size, pygame.SRCALPHA)
        self.aux_surf_size = pygame.math.Vector2(self.temp_size)
        self.aux_rect = self.aux_surf.get_rect(center = (self.half_p1_width, self.half_p1_height))

        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.aux_surf_size[0] // 2 - self.half_p1_width
        self.internal_offset.y = self.aux_surf_size[1] // 2 - self.half_p1_height

    def zoomfn(self):
        pressed_key = pygame.key.get_pressed()

        if self.zoom >= 0.1:
            if pressed_key[K_LEFTBRACKET] and not self.was_pressed[K_LEFTBRACKET]:
                self.zoom -= 0.05

        if self.zoom <= 1.95:
            if pressed_key[K_RIGHTBRACKET] and not self.was_pressed[K_RIGHTBRACKET]:
                self.zoom += 0.05

        self.was_pressed = pressed_key

    def display_sprites(self, p):
        self.aux_surf.fill('#000000')
        self.zoomfn()

        self.offset.xy = (p.rect.centerx - self.half_p1_width, p.rect.centery - self.half_p1_height)
        map_offset = self.map_rect.topleft - self.offset + self.internal_offset
        self.aux_surf.blit(self.map_surf, map_offset)

        sorted_sprites_list = sorted(self.sprites(), key = lambda sprite: sprite.rect.centery)
        for s in sorted_sprites_list:
            offset_pos = s.rect.topleft - self.offset + self.internal_offset
            self.aux_surf.blit(s.image, offset_pos)

        zoomed_surf_size = pygame.math.Vector2(self.zoom * self.aux_surf_size)
        zoomed_surf = pygame.transform.scale(self.aux_surf, zoomed_surf_size)
        zoomed_rect = zoomed_surf.get_rect(center = (self.half_p1_width, self.half_p1_height))		

        self.p1_surf.blit(zoomed_surf, zoomed_rect)

class MiniMap:
    def __init__(self, p1_surf):
        self.p1_surf = p1_surf

        self.p1_surf_w = config.P1_SCREEN_WIDTH
        self.p1_surf_h = config.P1_SCREEN_HEIGHT

        self.mini_map_width = self.p1_surf_w // 8
        self.mini_map_height = self.p1_surf_h // 8

        self.mini_map = pygame.Surface((self.mini_map_width, self.mini_map_height))
        self.mini_map_rect = self.mini_map.get_rect(topright = (config.P1_SCREEN_WIDTH - 2, 0))

        self.image = pygame.image.load('../graphics/detailed_map.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.mini_map_width, self.mini_map_height))	
        self.image_rect = self.image.get_rect(topright = (self.mini_map_width, 0))	
        self.image.fill((150, 150, 150), special_flags = pygame.BLEND_RGB_MULT) 

    def render_minimap(self, sprite_pos):		
        pygame.draw.rect(self.image, '#ffffff', self.image_rect, width = 2)
        self.mini_map.blit(self.image, self.image_rect)

        circle_center_x = float(sprite_pos[0] / config.MAP_SIZE[0]) * self.mini_map_width
        circle_center_y = float(sprite_pos[1] / config.MAP_SIZE[1]) * self.mini_map_height
        pygame.draw.circle(self.mini_map, (255,0,0), (circle_center_x, circle_center_y), 4)

        self.p1_surf.blit(self.mini_map, self.mini_map_rect)

class DayNightCycle:
    def __init__(self, p1_surf):
        self.p1_surf = p1_surf
        self.overlay_surf = pygame.Surface(config.P1_SIZE)

        self.morning_color = [255,255,255]
        self.evening_color = [50,50,50]
        self.current_color = self.morning_color.copy()

        self.daytime = True
        self.cycle_rate = 2

    def cycle(self, dt):
        self.check_daytime(dt)

        if self.daytime:
            for i in range(3):
                if (self.current_color[i] > self.evening_color[i]) and (self.current_color[i] - self.cycle_rate*dt > 0):
                    self.current_color[i] -= self.cycle_rate * dt
        else:
            for i in range(3):
                if (self.current_color[i] < self.morning_color[i]) and (self.current_color[i] + self.cycle_rate*dt < 255):
                    self.current_color[i] += self.cycle_rate * dt

        self.overlay_surf.fill(self.current_color)
        self.p1_surf.blit(self.overlay_surf, (0,0), special_flags = pygame.BLEND_RGB_MULT)

    def check_daytime(self, dt):
        for i in range(3):
            if self.current_color[i] < self.cycle_rate*dt + self.evening_color[i]:
                self.daytime = False
            elif self.current_color[i] > self.morning_color[i] - 1.5*self.cycle_rate*dt:
                self.daytime = True
                return


class TextBox:
    def __init__(self, font_size, width, height):
        self.surf = pygame.display.get_surface()
        self.font = config.game_font(font_size)

        self.rect_width = width
        self.rect_height = height

        self.text = []
        self.snip = self.font.render('', True, 'white')
        self.snip_rect = self.snip.get_rect()

        self.typing_speed = 10

        self.bg_rect = pygame.rect.Rect([(config.SCREEN_WIDTH-self.rect_width)//2, (config.SCREEN_HEIGHT-self.rect_height)//2, self.rect_width, self.rect_height])

    def disp_textbox(self, aux_surf):
        pygame.draw.rect(aux_surf, 'white', self.bg_rect)
        pygame.Surface.fill(aux_surf, color = (235,236,240), rect = self.bg_rect, special_flags = pygame.BLEND_RGBA_MULT)

    def typewriter_effect(self, aux_surf):
        for j in range(len(self.text)):
            index = 0
            while True:
                # event handler
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()

                self.disp_textbox(aux_surf)

                if index < len(self.text[j]) * self.typing_speed:
                    index += 1
                else:
                    break

                self.snip = self.font.render(self.text[j][0:(index // self.typing_speed)], True, (20,109,153))
                self.snip_rect = self.snip.get_rect(center = self.bg_rect.center)

                aux_surf.blit(self.snip, self.snip_rect)
                self.surf.blit(aux_surf, (0,0))

                pygame.display.flip()

            if not (j==2 or j==4 or j==7):
                sleep(0.75)
            else:
                sleep(1.25)
            self.snip = self.font.render('', True, 'white')

        sleep(1.5)

class Introduction(TextBox):
    def __init__(self, font_size = 40, width = 1000, height = 200):
        self.surf = pygame.display.get_surface()
        super().__init__(font_size, width, height)

        self.text = ['During the UP state elections of 2002,',
                    'politician Ramlal visited village Prempur,',
                    'where people live in abject poverty.',

                    'Ramlal promised water and resources',
                    'to the people of Prempur in his campaign.',

                    'Though the elders had long grown inured',
                    'to these fake promises,',
                    'Chotu was hopeful.',

                    'Can you help keep Chotu\'s hopes?']

        self.image = pygame.image.load('../graphics/detailed_map.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))	
        self.image_rect = self.image.get_rect()	
        self.image.fill((150, 150, 150), special_flags = pygame.BLEND_RGB_MULT)

    def render_intro(self):
        self.surf.blit(self.image, self.image_rect)
        self.typewriter_effect(self.surf)
        self.surf.fill('black')

class DayOne(TextBox):
    def __init__(self, p1_surf):
        self.surf = pygame.display.get_surface()
        self.p1_surf = p1_surf

        super().__init__(40,650,75)
        self.text = ['Day One']
        self.bg_rect.x = (config.P1_SCREEN_WIDTH-self.rect_width)//2
        self.bg_rect.y = (config.P1_SCREEN_HEIGHT-self.rect_height)//2

    def run_day(self):
        self.typewriter_effect(self.p1_surf)
        self.text = ['Yay, it rained today!', 'I should get water from the well.']