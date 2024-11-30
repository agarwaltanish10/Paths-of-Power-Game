import pygame, os, random
from time import sleep
from pygame.locals import *
from support import Timer
import config

class Player(pygame.sprite.Sprite):
	def __init__(self, group, pos, collision_group, fruit_sprites, fruit_pos):
		super().__init__(group)

		self.curr_status = 'boy_idle'
		self.curr_frame = 0
		self.import_assets()
		
		self.image = self.graphics[self.curr_status][self.curr_frame]
		self.rect = self.image.get_rect(center = pos)

		self.hitbox = self.rect.copy()
		self.hitbox.inflate_ip(-26,-42)
		self.collision_group = collision_group

		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(self.rect.center)
		self.vel = 200 # change

		self.facing_left = False
		self.last_key_left = False

		# tools
		self.tool_list = ['bucket', 'basket']
		self.selected_tool = self.tool_list[1]
		self.timer = Timer(500, self.use_tool)

		self.fruit_sprites = fruit_sprites
		self.target = pygame.math.Vector2(self.rect.center)
		self.fruit_pos = fruit_pos

		self.was_pressed = pygame.K_TAB

	def import_assets(self):
		self.assets = ['boy', 'bucket', 'basket']

		self.graphics = {
	    'boy': [], 'boy_idle': [], 'boy_walk': [],
		'bucket': [], 'bucket_use': [], 
		'basket': [], 'basket_use': []
	    }

		i,j = 0,0
		for c in self.assets:
			dict_keys = list(self.graphics.keys())

			if j+3 <= len(dict_keys):
				for i in range(j, j+3):
					if i <= 2:
						full_path = f'../graphics/villagers/{c}/{dict_keys[i]}'
					else:
						full_path = f'../graphics/tools/{dict_keys[i]}'

					for img_file_name in sorted(os.listdir(full_path)):
						curr_path = full_path + f'/{img_file_name}'
						img_surf = pygame.image.load(curr_path).convert_alpha()
						img_surf = pygame.transform.rotozoom(img_surf, 0, 2)
						self.graphics[dict_keys[i]].append(img_surf)

			j = i+1

	def check_collided(self):
		for s in self.collision_group.sprites():
			if s.hitbox.colliderect(self.hitbox):
				# if player moving left and corresponding edges of hitboxes come in contact
				if self.direction.x < 0 and not(self.hitbox.left <= s.hitbox.left):
					self.hitbox.left = s.hitbox.right
				# if player moving right and corresponding edges of hitboxes come in contact
				elif self.direction.x > 0 and not(self.hitbox.right >= s.hitbox.right):
					self.hitbox.right = s.hitbox.left

				# if player moving down and corresponding edges of hitboxes come in contact
				if self.direction.y > 0 and not(self.hitbox.bottom >= s.hitbox.bottom):
					self.hitbox.bottom = s.hitbox.top
				# if player moving up and corresponding edges of hitboxes come in contact
				elif self.direction.y < 0 and not(self.hitbox.top <= s.hitbox.top):
					self.hitbox.top = s.hitbox.bottom

				self.pos = pygame.math.Vector2(self.hitbox.centerx, self.hitbox.centery)
				self.rect.center = self.hitbox.center

	def update_pos(self, dt):
		pressed_keys = pygame.key.get_pressed()

		if not self.timer.is_active:
			if pressed_keys[pygame.K_RIGHT]:
				self.direction.x = 1
				self.last_key_left = False
			elif pressed_keys[pygame.K_LEFT]:
				self.direction.x = -1
				self.last_key_left = True
			else:
				self.direction.x = 0

			if pressed_keys[pygame.K_UP]:
				self.direction.y = -1
			elif pressed_keys[pygame.K_DOWN]:
				self.direction.y = 1
			else:
				self.direction.y = 0

			if self.direction.x != 0 and self.direction.y != 0:
				self.direction = self.direction.normalize()

			self.pos.x += dt * self.direction.x * self.vel
			self.pos.y += dt * self.direction.y * self.vel
			self.rect.center = (round(self.pos.x), round(self.pos.y))

			self.hitbox.center = self.rect.center
			self.check_collided()

		if pressed_keys[pygame.K_SLASH]:
			self.timer.activate_timer()
			self.direction = pygame.math.Vector2()
			# self.curr_frame = 0

		if pressed_keys[pygame.K_SPACE] and not self.was_pressed[pygame.K_SPACE]:
			if self.selected_tool == self.tool_list[0]:
				self.selected_tool = self.tool_list[1]
			elif self.selected_tool == self.tool_list[1]:
				self.selected_tool = self.tool_list[0]

		self.was_pressed = pressed_keys

	def animations(self, dt):
		split_status = self.curr_status.split('_')
		if self.direction.x == 0 and self.direction.y == 0:
			self.curr_status = 'boy_idle'
		else:
			self.curr_status = 'boy_walk'

		if self.timer.is_active:
			self.curr_status = self.selected_tool + '_use'

		total_frames = len(self.graphics[self.curr_status])
		self.curr_frame += 2*dt
		self.curr_frame %= total_frames

		self.image = self.graphics[self.curr_status][int(self.curr_frame)]
		self.flip_image()

	def flip_image(self):
		pressed_keys = pygame.key.get_pressed()

		if (pressed_keys[K_RIGHT] and self.facing_left == True):
			self.image = pygame.transform.flip(self.image, True, False)
			self.facing_left = False

		if (pressed_keys[K_LEFT] and self.facing_left == False) or (self.last_key_left == True):
			self.image = pygame.transform.flip(self.image, True, False)
			self.facing_left = True

	def get_target(self):
		self.target[0] = self.rect.centerx + 5
		self.target[1] = self.rect.centery

	def use_tool(self):
		self.inflated_rect = pygame.Rect.inflate(self.rect, self.rect.width + 10, self.rect.height + 10)
		if self.selected_tool == 'basket':
			for f in self.fruit_sprites.sprites():
				if f.rect.colliderect(self.inflated_rect):
					f.grab_fruit(self.inflated_rect.center)

		elif self.selected_tool == 'bucket':
			pass

	def update(self, dt):
		self.update_pos(dt)
		self.timer.update_status_timer()	
		self.get_target()	
		self.animations(dt)

		return self.pos

class MapObject(pygame.sprite.Sprite):
	def __init__(self, surf, group, pos, w, h, scale_w = 0.1, scale_h = 0.5):
		super().__init__(group)
		self.image = pygame.transform.scale(surf, (w, h))
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.copy()
		self.hitbox.inflate_ip(-self.rect.width * scale_w, -self.rect.height * scale_h)

class Fence(MapObject):
	def __init__(self, surf, group, position):
		super().__init__(surf, group, position, surf.get_size()[0], surf.get_size()[1], 0, 0)

class Tree(MapObject):
	def __init__(self, surf, group, position, width, height):
		super().__init__(surf, group, position, width, height, 0.4, 0.5)
			
class Flash(pygame.sprite.Sprite):
	def __init__(self, pos, surf, group):
		super().__init__(group)
		print(group)

		self.start_time = pygame.time.get_ticks()
		self.duration = 500

		self.image = surf
		self.rect = self.image.get_rect(center = pos)
		mask_surf = pygame.mask.from_surface(self.image)
		new_surf = mask_surf.to_surface()
		new_surf.set_colorkey((0,0,0))
		self.image = new_surf

		self.rect = self.image.get_rect(center = pos)
  
	def update(self, dt):
		if pygame.time.get_ticks() - self.start_time > self.duration:
			self.kill()

class Fruit(pygame.sprite.Sprite):
	def __init__(self, group, centerpos, fruit_sprites):
		super().__init__(group)
		self.image = pygame.image.load('../graphics/cherry.jpg').convert_alpha()
		self.image = pygame.transform.scale_by(self.image, 0.2)
		self.rect = self.image.get_rect(center = centerpos)
		self.fruit_sprites = fruit_sprites

	def grab_fruit(self, target):
		distances = [abs(target[1] - self.fruit_sprites.sprites()[iter].rect.center[1]) for iter in range(len(self.fruit_sprites))]
		min_distance = 100000
		argmin_distance = 0

		for i in range(len(self.fruit_sprites)):
			if distances[i] < min_distance:
				min_distance = distances[i]
				argmin_distance = i

		if len(self.fruit_sprites) > 0:
			grabbed_fruit = self.fruit_sprites.sprites()[argmin_distance]
			Flash(grabbed_fruit.rect.center, grabbed_fruit.image, self.groups()[0])
			grabbed_fruit.kill()






