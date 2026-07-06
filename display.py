import pygame
import sys


class Display:
	SCREEN_WIDTH = 1920
	SCREEN_HEIGHT = 1080
	FPS = 60
	MIN_ZOOM = 0.5
	MAX_ZOOM = 3.0
	zoom_scale = 1

	def _display_hub(self, screen, coords: list, color):
		colors = {
			'red': (255, 0, 0),
			'blue': (0, 0, 255),
			'green': (0, 128, 0),
			'cyan': (0, 255, 255),
			'orange': (255, 165, 0),
			'gold': (255, 215, 0)}
		if color and color in colors:
			pygame.draw.rect(screen, colors[color], ((coords[0]*100) + 400, (coords[1] * 100) + 300, 50, 50))
		else:
			pygame.draw.rect(screen, (255, 255, 255), ((coords[0]*100) + 400, (coords[1] * 100) + 300, 50, 50))

	def _display_connection(self):
		pass

	def display(self, nodes: dict):
		pygame.init()
		screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
		pygame.display.set_caption("Fly-in")
		clock = pygame.time.Clock()
		running = True
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				# elif event.type == pygame.MOUSEWHEEL:
            	# 	zoom_scale += event.y * 0.1
				# 	zoom_scale = max(MIN_ZOOM, min(zoom_scale, MAX_ZOOM))
			screen.fill((50, 50, 50)) #background color
			#moves tracker
			pygame.draw.rect(screen, (30, 30, 30), (0, 0, 360, 1080))
			#the hubs
			for key, value in nodes.items():
				self._display_hub(screen, nodes[key]['coords'], nodes[key]['color'])
			pygame.display.flip()
			clock.tick(self.FPS)
		pygame.quit()
		sys.exit()

if __name__ == "__main__":
	display = Display()
	network = {}
	display.display(network['nodes'])