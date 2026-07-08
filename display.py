import pygame
import sys


class Display:
	SCREEN_WIDTH = 1920
	SCREEN_HEIGHT = 1080
	FPS = 60

	def _display_hub(self, screen, coords: list, color):
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
		y = (coords[1] * 120) + 500

		draw_color = colors.get(color, (255, 255, 255))
		pygame.draw.rect(screen, draw_color, (x - 25, y - 25, 50, 50))

	def _display_connection(self, screen, current_coords: list, neighbor_name: str, all_nodes: dict):
		if neighbor_name in all_nodes:
			neighbor_coords = all_nodes[neighbor_name]['coords']
			
			start_x = (current_coords[0] * 120) + 400
			start_y = (current_coords[1] * 120) + 500
			
			end_x = (neighbor_coords[0] * 120) + 400
			end_y = (neighbor_coords[1] * 120) + 500
			
			pygame.draw.line(screen, (150, 150, 150), (start_x, start_y), (end_x, end_y), 3)

	def _display_drone(self, screen, node_coords: list, nb_drones, drone_img):
		x = (node_coords[0] * 120) + 400
		y = (node_coords[1] * 120) + 500
		drone_img = pygame.transform.scale(drone_img, (50, 50))
		if nb_drones > 0:
			screen.blit(drone_img, (x - 25, y - 25))

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
			screen.fill((50, 50, 50)) # background color
			# moves tracker
			# pygame.draw.rect(screen, (30, 30, 30), (0, 0, 360, 1080))
			# connections
			for node_name, node_data in nodes.items():
				for neighbor_name in node_data['neighbors'].keys():
					self._display_connection(screen, node_data['coords'], neighbor_name, nodes)
			#the hubs
			for key, value in nodes.items():
				self._display_hub(screen, nodes[key]['coords'], nodes[key]['color'])
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
