import pygame
import sys
from parser import FileParser
from logic import SolutionLogic
from data import Network, Drone, Zone


class Flyin:

    def parse(self, file):
        parser = FileParser(file)
        network = dict()
        try:
            parser.read_file()
            network = parser.parse()
            metadata = Network(network)
            network = metadata.update(network)
        except (ValueError, FileNotFoundError) as e:
            print(e)
        return network

    def produce_drones(self, nb_drones):
        drone_list = []
        for _ in range(nb_drones):
            drone_list.append(Drone("start"))
        return drone_list


class Simulation:

    def __init__(self, network):
        self.SCREEN_WIDTH = 1920
        self.SCREEN_HEIGHT = 1080
        self.FPS = 60

        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Fly-in")
        self.clock = pygame.time.Clock()

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
            'magenta': (255, 0, 255),
            'black': (0, 0, 0),
            'maroon': (128, 0, 0),
            'darkred': (139, 0, 0),
            'violet': (238, 130, 238),
            'crimson': (220, 20, 60),
            'rainbow': (255, 255, 255)
        }

        x = (coords[0] * 120) + 400
        y = 500 - (coords[1] * 120)

        hub_name = name
        hub_circle = pygame.Rect(x, y, 0, 0)
        font = pygame.font.Font(None, 14)
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

    def _display_drone(self, screen, node_coords: list):
        x = (node_coords[0] * 120) + 400
        y = 500 - (node_coords[1] * 120)
        center_x, center_y = x, y
        width, height = 40, 40
        top    = (center_x, center_y - height // 2)
        right  = (center_x + width // 2, center_y)
        bottom = (center_x, center_y + height // 2)
        left   = (center_x - width // 2, center_y)
        pygame.draw.polygon(screen, (60, 60, 60), [top, right, bottom, left])

    def update_simulation_state(self, solution: SolutionLogic):
        solution.next_move()


    def draw(self, nodes, drones):
        self.screen.fill((255, 255, 255))

        for node_name, node_data in nodes.items():
            for neighbor_name in node_data['neighbors'].keys():
                self._display_connection(self.screen, node_data['coords'], neighbor_name, nodes)

        for key, value in nodes.items():
            self._display_hub(self.screen, nodes[key]['coords'], key, nodes[key]['color'])

        for drone in drones:
            self._display_drone(self.screen, nodes[drone.position]['coords'])

        pygame.display.flip()

    def run(self, nodes, solution: SolutionLogic):
        running = True
        count = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.update_simulation_state(solution)
                        print(count)
                        count += 1

            self.draw(nodes, solution.drones)

            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    fly_in = Flyin()
    network = Network.parse("02_capacity_hell.txt")
    solution = SolutionLogic(network)
    simulation = Simulation(network)
    simulation.run(network['zones'], solution)

