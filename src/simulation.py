from __future__ import annotations

import sys
from typing import Any

import pygame

from src.logic import SolutionLogic


class Simulation:
    """Render and run the drone movement simulation with Pygame."""

    COLORS = {
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "green": (0, 128, 0),
        "cyan": (0, 255, 255),
        "orange": (255, 165, 0),
        "gold": (255, 215, 0),
        "purple": (128, 0, 128),
        "yellow": (255, 255, 0),
        "brown": (165, 42, 42),
        "lime": (0, 255, 0),
        "magenta": (255, 0, 255),
        "black": (50, 50, 50),
        "maroon": (128, 0, 0),
        "darkred": (139, 0, 0),
        "violet": (238, 130, 238),
        "crimson": (220, 20, 60),
        "rainbow": (255, 255, 255),
    }

    def __init__(self) -> None:
        """Initialize the simulation window and drawing state."""
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.FPS = 60
        self.PADDING = 80
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.min_x = 0.0
        self.max_y = 0.0

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption("Fly-in")
        self.clock = pygame.time.Clock()

    def _update_viewport(self, zones: dict[str, Any]) -> None:
        """Compute the drawing scale and offsets for the current zones."""
        width, height = self.screen.get_size()
        xs = [zone.coords[0] for zone in zones.values()]
        ys = [zone.coords[1] for zone in zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        usable_w = max(width - 2 * self.PADDING, 1)
        usable_h = max(height - 2 * self.PADDING, 1)

        self.scale = min(usable_w / span_x, usable_h / span_y)
        self.min_x = min_x
        self.max_y = max_y
        content_w = span_x * self.scale
        content_h = span_y * self.scale
        self.offset_x = (width - content_w) / 2
        self.offset_y = (height - content_h) / 2

    def _to_screen(self, coords: list[float]) -> tuple[float, float]:
        """Convert map coordinates into screen coordinates."""
        x = self.offset_x + (coords[0] - self.min_x) * self.scale
        y = self.offset_y + (self.max_y - coords[1]) * self.scale
        return x, y

    def _hub_radius(self) -> int:
        """Return the radius used to draw hubs."""
        return max(8, int(self.scale * 0.35))

    def _drone_size(self) -> int:
        """Return the size used to draw drones."""
        return max(8, int(self.scale * 0.35))

    def _display_hub(self, zone: Any) -> None:
        """Draw a single hub and its label."""
        x, y = self._to_screen(zone.coords)
        radius = self._hub_radius()

        font = pygame.font.Font(None, max(12, int(radius * 0.5)))
        text_surface = font.render(zone.name, True, (0, 0, 0))
        hub_text = text_surface.get_rect(center=(x, y))

        draw_color = self.COLORS.get(zone.color, (255, 255, 255))
        pygame.draw.circle(self.screen, draw_color, (int(x), int(y)), radius)
        self.screen.blit(text_surface, hub_text)

    def _display_connection(
        self,
        zone: Any,
        neighbor_name: str,
        zones: dict[str, Any],
        drones: list[Any]
    ) -> None:
        """Draw a connection line between two neighboring hubs."""
        neighbor = zones.get(neighbor_name)
        if neighbor is None:
            return

        start = self._to_screen(zone.coords)
        end = self._to_screen(neighbor.coords)

        line_width = max(1, int(self.scale * 0.03))
        pygame.draw.line(self.screen, (150, 150, 150), start, end, line_width)

    def _display_drone_at(self, x: float, y: float) -> None:
        """Draw a drone marker at the given screen position."""
        size = self._drone_size()
        top = (x, y - size // 2)
        right = (x + size // 2, y)
        bottom = (x, y + size // 2)
        left = (x - size // 2, y)
        pygame.draw.polygon(
            self.screen,
            (60, 60, 60),
            [top, right, bottom, left],
        )

    def _display_drone(self, zone: Any) -> None:
        """Draw a drone at the coordinates of the given zone."""
        x, y = self._to_screen(zone.coords)
        self._display_drone_at(x, y)

    def _display_move_count(self, move_count: int) -> None:
        """Draw the current move counter in the top-left corner."""
        font = pygame.font.Font(None, 36)
        text_surface = font.render(
            f"Move Count: {move_count}",
            True,
            (0, 0, 0),
        )
        self.screen.blit(text_surface, (10, 10))

    def update_simulation_state(self, solution: SolutionLogic) -> None:
        """Advance the simulation by one movement step."""
        reach_goal = True
        solution.next_move()
        for drone in solution.drones:
            if drone.position != solution.dest:
                reach_goal = False
        if not reach_goal:
            solution.move_count += 1

    def draw(self, solution: SolutionLogic) -> None:
        """Render the current simulation state to the screen."""
        self.screen.fill((255, 255, 255))
        zones = solution.zones
        self._update_viewport(zones)

        for zone in zones.values():
            for neighbor_name in zone.neighbors:
                self._display_connection(zone,
                                         neighbor_name,
                                         zones, solution.drones)

        for zone in zones.values():
            self._display_hub(zone)

        for drone in solution.drones:
            if drone.connection_from and drone.connection_to:
                start = zones[drone.connection_from].coords
                end = zones[drone.connection_to].coords
                mid_coords = [
                    (start[0] + end[0]) / 2,
                    (start[1] + end[1]) / 2,
                ]
                mid_x, mid_y = self._to_screen(mid_coords)
                self._display_drone_at(mid_x, mid_y)
                continue
            self._display_drone(zones[drone.position])
        if solution.move_count < 0:
            self._display_move_count(0)
        else:
            self._display_move_count(solution.move_count)
        pygame.display.flip()

    def run(self, solution: SolutionLogic) -> None:
        """Start the event loop and run the simulation until exit."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.SCREEN_WIDTH, self.SCREEN_HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
                        pygame.RESIZABLE,
                    )

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.update_simulation_state(solution)

            self.draw(solution)
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()
