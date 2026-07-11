import pygame
import sys


class Display:
	SCREEN_WIDTH = 1920
	SCREEN_HEIGHT = 1080
	FPS = 60

	def _display_hub(self, screen, coords: list, name: str, color):
		colors = {
			'red': (255, 0, 0),
			'blue': (0, 0, 255),
			'green': (0, 128, 0),
			'cyan': (0, 255, 255),
			'orange': (255, 165, 0),
			'gold': (255, 215, 0),
			'purple': (128, 0, 128),
			'yellow': (255, 255, 0),
			'brown': (165, 42, 42),
			'lime': (0, 255, 0),
			'magenta': (255, 0, 255)
		}

		# Centering adjustment: Map and scale layout coordinates
		x = (coords[0] * 120) + 400
		y = 500 - (coords[1] * 120)

		hub_name = name
		hub_circle = pygame.Rect(x, y, 0, 0)
		font = pygame.font.Font(None, 20)
		text_surface = font.render(hub_name, True, (0, 0, 0))
		hub_text = text_surface.get_rect()
		hub_text.center = hub_circle.center

		draw_color = colors.get(color, (255, 255, 255))
		pygame.draw.circle(screen, draw_color, (x, y), 40)
		screen.blit(text_surface, hub_text) 

	def _display_connection(self, screen, current_coords: list, neighbor_name: str, all_nodes: dict):
		if neighbor_name in all_nodes:
			neighbor_coords = all_nodes[neighbor_name]['coords']
			
			start_x = (current_coords[0] * 120) + 400
			start_y = 500 - (current_coords[1] * 120)
			
			end_x = (neighbor_coords[0] * 120) + 400
			end_y = 500 - (neighbor_coords[1] * 120)
			
			pygame.draw.line(screen, (150, 150, 150), (start_x, start_y), (end_x, end_y), 3)

	def _display_drone(self, screen, node_coords: list, nb_drones, drone_img):
		x = (node_coords[0] * 120) + 400
		y = 500 - (node_coords[1] * 120)
		drone_img = pygame.transform.scale(drone_img, (50, 50))
		if nb_drones > 0:
			center_x, center_y = x, y
			width, height = 40, 40
			top    = (center_x, center_y - height // 2)
			right  = (center_x + width // 2, center_y)
			bottom = (center_x, center_y + height // 2)
			left   = (center_x - width // 2, center_y)
			pygame.draw.polygon(screen, (60, 60, 60), [top, right, bottom, left])

	def display(self, nodes: dict):
		pygame.init()
		screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
		pygame.display.set_caption("Fly-in")
		clock = pygame.time.Clock()
		drone_img = pygame.image.load("drone.png").convert_alpha()
		running = True
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
			screen.fill((255, 255, 255)) # background color
			# connections
			for node_name, node_data in nodes.items():
				for neighbor_name in node_data['neighbors'].keys():
					self._display_connection(screen, node_data['coords'], neighbor_name, nodes)
			#the hubs
			for key, value in nodes.items():
				self._display_hub(screen, nodes[key]['coords'], key, nodes[key]['color'])
			
			#drones
			for key, value in nodes.items():
				self._display_drone(screen, nodes[key]['coords'], nodes[key]['nb_drones'], drone_img)
			pygame.display.flip()
			clock.tick(self.FPS)
		pygame.quit()
		sys.exit()

if __name__ == "__main__":
	display = Display()
	network = {}
	display.display(network['nodes'])
