import pygame, sys, random
from pygame.locals import *
from time import sleep
from level import Level, Introduction
from launcher import Menu, MenuButton, LoadingBar
import config

class Game:
	def __init__(self):
		
		screen_res = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
		# self.screen = pygame.display.set_mode((1220,1220))
		self.screen = pygame.display.set_mode(screen_res, flags = pygame.SCALED)
		pygame.display.set_caption('Paths of Power')

		self.p1_surf = pygame.Surface((config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT))
		self.p2_surf = pygame.Surface((config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT))	

		config.P1_SIZE = self.p1_surf.get_size()
		config.P2_SIZE = self.p2_surf.get_size()

		config.P1_SCREEN_WIDTH = config.P1_SIZE[0]
		config.P1_SCREEN_HEIGHT = config.P1_SIZE[1]

		config.P2_SCREEN_WIDTH = config.P2_SIZE[0]
		config.P2_SCREEN_HEIGHT = config.P2_SIZE[1]

		self.level = Level(self.p1_surf, self.p2_surf)
		self.clock = pygame.time.Clock()	
		self.intro = Introduction()

		# setup details
		self.font = config.game_font(64)
		self.return_main_menu = False
		self.gameplay = False
		self.loading_screen = True
		self.load_introduction = True

	def play(self, dt):
		while True:
			pygame.display.set_caption('Paths of Power')
			# event handler
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						self.return_main_menu = True
						break

			if self.return_main_menu:
				break

			if self.load_introduction:
				self.intro.render_intro()
				self.load_introduction = False	

			# self.screen.fill('black')
			self.p1_surf.fill('black') 
			self.p2_surf.fill('black')

			self.level.run_level(dt)

			self.screen.blit(self.p1_surf, (0,0))
			self.screen.blit(self.p2_surf, (config.SCREEN_WIDTH // 2,0))
			
			pygame.display.flip()

		self.menu()
		# self.load_introduction = True

	def settings(self):
		while True:
			# event handler
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False
					pygame.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						self.return_main_menu = True
						break
					
			if self.return_main_menu:
				break
			
			self.screen.fill('black')
			pygame.display.set_caption('Settings')
			
			settings_text = self.font.render('This is the settings screen. Press Esc to return to menu.', True, 'white')
			settings_rect = settings_text.get_rect(center = (640, 260))
			self.screen.blit(settings_text, settings_rect)
			
			pygame.display.flip()
			
		self.menu()

	def help_screen(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False
					pygame.quit()
					sys.exit()
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						self.return_main_menu = True
						break
					
			if self.return_main_menu:
				break
			
			self.screen.fill('black')
			pygame.display.set_caption('Help')
			
			settings_text = self.font.render('This is the help screen. Press Esc to return to menu.', True, 'white')
			settings_rect = settings_text.get_rect(center = (640, 260))
			self.screen.blit(settings_text, settings_rect)
			
			pygame.display.flip()
			
		self.menu()

	def menu(self):
		self.return_main_menu = False
		self.screen.fill('black')

		mouse_pos = pygame.mouse.get_pos()
		text_xpos = config.SCREEN_WIDTH // 2
		
		main_menu = Menu()
		main_menu.display_menu()

		self.menu_buttons = [None] * 4
		
		self.menu_buttons[0] = MenuButton('Play', 300)
		self.menu_buttons[1] = MenuButton('Settings', 400)
		self.menu_buttons[2] = MenuButton('Help', 500)
		self.menu_buttons[3] = MenuButton('Quit', 600)

		for button in self.menu_buttons:
			button.display_text(mouse_pos)

	def loading(self):
		loading_bar = LoadingBar()
		i = 1
		while i <= 100:
			self.screen.fill('black')
			multiplier = random.uniform(1,1.5)
			loading_bar.drawBar(multiplier * i / 100)
			i *= multiplier
			pygame.display.flip()
			sleep(multiplier / 10)

		self.loading_screen = False

	def run_game(self):
		while True:
			dt = self.clock.tick(60) / 1000

			# self.screen.fill('black')			

			# self.play(dt)

			if self.loading_screen:
				self.loading()
			self.menu()

			# event handler
			mouse_pos = pygame.mouse.get_pos()
			for event in pygame.event.get():
				if (event.type == QUIT) or (event.type == MOUSEBUTTONDOWN and self.menu_buttons[3].check_mouse_pos(mouse_pos)):
					pygame.quit()
					sys.exit()

				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						pygame.quit()
						sys.exit()

				if event.type == MOUSEBUTTONDOWN:
					if self.menu_buttons[0].check_mouse_pos(mouse_pos):
						self.play(dt)
					elif self.menu_buttons[1].check_mouse_pos(mouse_pos):
						self.settings()
					elif self.menu_buttons[2].check_mouse_pos(mouse_pos):
						self.help_screen()
				
			pygame.display.flip()

if __name__ == '__main__':

	pygame.init()
	
	infoObject = pygame.display.Info()
	config.SCREEN_WIDTH = infoObject.current_w
	config.SCREEN_HEIGHT = infoObject.current_h

	game = Game()
	game.run_game()