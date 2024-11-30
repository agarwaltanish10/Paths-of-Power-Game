import pygame, sys
import config

class Menu:
	def __init__(self):
		self.surf = pygame.display.get_surface()
		self.font = config.game_font(64)
		self.xpos = config.SCREEN_WIDTH // 2

		self.text = self.font.render('Main Menu', True, (0,0,0))
		self.text_rect = self.text.get_rect(center = (self.xpos, 200))

		self.bg = pygame.image.load('../graphics/map.png').convert_alpha()
		self.bg = pygame.transform.scale(self.bg, (self.bg.get_size()[0] * 1.3, self.bg.get_size()[1] * 1.2))
		self.bg.fill((48, 48, 48), special_flags = pygame.BLEND_RGB_ADD)
		self.bg_rect = self.bg.get_rect(center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))

	def display_menu(self):
		self.surf.blit(self.bg, self.bg_rect)
		pygame.draw.rect(self.surf, (220, 220, 220), pygame.Rect(self.xpos - 250, 100, 490, 585))
		self.surf.blit(self.text, self.text_rect)

class MenuButton:
	def __init__(self, button_text, text_ypos, textcolor = 'black'):
		self.surf = pygame.display.get_surface()
		self.font = pygame.font.Font('../fonts/minecraft.ttf', 32)
		self.pos = (config.SCREEN_WIDTH // 2, text_ypos)

		self.button_text = button_text
		self.textcolor = textcolor

		self.text = self.font.render(self.button_text, True, self.textcolor)
		self.text_rect = self.text.get_rect(center = self.pos)
		self.inflated_rect = self.text_rect.inflate(self.text_rect.width * 0.75, self.text_rect.height * 20)

	def display_text(self, mouse_pos):
		if self.check_mouse_pos(mouse_pos):
			self.text = self.font.render(self.button_text, True, 'red')
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

		if (mouse_pos[0] <= self.inflated_rect.left or mouse_pos[0] >= self.inflated_rect.right) or (mouse_pos[1] >= self.inflated_rect.bottom or mouse_pos[1] <= self.inflated_rect.top):
			self.text = self.font.render(self.button_text, True, self.textcolor)
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

		self.surf.blit(self.text, self.text_rect)

	def check_mouse_pos(self, mouse_pos):
		if (mouse_pos[0] >= self.text_rect.left and mouse_pos[0] <= self.text_rect.right):
			if (mouse_pos[1] <= self.text_rect.bottom and mouse_pos[1] >= self.text_rect.top):
				return True
		else:
			return False

class LoadingBar:
	def __init__(self):
		self.surf = pygame.display.get_surface()
		self.screen_halfw = config.SCREEN_WIDTH // 2
		self.screen_halfh = config.SCREEN_HEIGHT // 2
		self.barsize = [400, 60]
		self.barpos = [self.screen_halfw - self.barsize[0] // 2, self.screen_halfh - self.barsize[1] // 2]

	def drawBar(self, progress):
		if progress > 1:
			progress = 1
		inner_barsize = [(self.barsize[0]-20) * progress, self.barsize[1]-20]
		
		pygame.draw.rect(self.surf, (255,255,255), pygame.Rect(self.barpos[0], self.barpos[1], self.barsize[0], self.barsize[1]), width = 2)
		pygame.draw.rect(self.surf, (124,252,0), pygame.Rect(self.barpos[0]+10, self.barpos[1]+10, inner_barsize[0], inner_barsize[1]), width = 0)
	
