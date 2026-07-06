import pygame
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zoom and Pan Canvas")
clock = pygame.time.Clock()

# --- CAMERA STATE ---
# Camera offset (scroll position) in world coordinates
camera_x = 0
camera_y = 0
# Zoom factor (1.0 = 100%, 2.0 = 200%, etc.)
zoom_level = 1.0

# --- WORLD DATA ---
# Define rectangles in "World Space": (x, y, width, height, color)
# These coordinates never change, no matter how much you zoom or pan!
world_rects = [
    (100, 100, 200, 150, (255, 0, 0)),    # Red Rect
    (400, 300, 150, 100, (0, 255, 0)),    # Green Rect
    (-200, -100, 300, 200, (0, 0, 255)),  # Blue Rect
    (0, 0, 50, 50, (255, 255, 255)),      # White Rect at World Origin (0,0)
]

# Panning state
is_panning = False
pan_start_mouse = (0, 0)
pan_start_camera = (0, 0)

# Main game loop
while True:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # --- PANNING (Scroll) CONTROLS ---
        # Using Middle Mouse Button to drag and pan
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            is_panning = True
            pan_start_mouse = mouse_pos
            pan_start_camera = (camera_x, camera_y)
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            is_panning = False
            
        # --- ZOOM CONTROLS ---
        elif event.type == pygame.MOUSEWHEEL:
            # Determine zoom direction
            zoom_factor = 1.1 if event.y > 0 else 0.9
            
            # --- Zoom to Mouse Position Math ---
            # 1. Find where the mouse is pointing in the World right now
            mouse_world_x = (mouse_pos[0] / zoom_level) + camera_x
            mouse_world_y = (mouse_pos[1] / zoom_level) + camera_y
            
            # 2. Apply the zoom change
            zoom_level *= zoom_factor
            # Clamp zoom so it doesn't go to infinity or negative
            zoom_level = max(0.1, min(zoom_level, 10.0)) 
            
            # 3. Adjust camera so the mouse stays over the same world point
            camera_x = mouse_world_x - (mouse_pos[0] / zoom_level)
            camera_y = mouse_world_y - (mouse_pos[1] / zoom_level)

    # Handle ongoing dragging for panning
    if is_panning:
        # Calculate how far the mouse moved
        dx = mouse_pos[0] - pan_start_mouse[0]
        dy = mouse_pos[1] - pan_start_mouse[1]
        # Adjust camera based on zoom (move slower when zoomed in, faster when zoomed out)
        camera_x = pan_start_camera[0] - dx / zoom_level
        camera_y = pan_start_camera[1] - dy / zoom_level

    # --- DRAWING ---
    screen.fill((30, 30, 30)) # Dark gray background

    # Draw grid lines to make scrolling/zooming obvious
    grid_size = 100
    # A simple way to draw a localized grid based on camera
    start_x = int(camera_x // grid_size) * grid_size - 1000
    end_x = start_x + 3000
    start_y = int(camera_y // grid_size) * grid_size - 1000
    end_y = start_y + 3000
    
    for x in range(int(start_x), int(end_x), grid_size):
        screen_x = int((x - camera_x) * zoom_level)
        pygame.draw.line(screen, (50, 50, 50), (screen_x, 0), (screen_x, HEIGHT))
    for y in range(int(start_y), int(end_y), grid_size):
        screen_y = int((y - camera_y) * zoom_level)
        pygame.draw.line(screen, (50, 50, 50), (0, screen_y), (WIDTH, screen_y))

    # Draw the World Objects
    for wx, wy, w_width, w_height, color in world_rects:
        # Convert World Coordinates to Screen Coordinates
        screen_x = int((wx - camera_x) * zoom_level)
        screen_y = int((wy - camera_y) * zoom_level)
        screen_w = int(w_width * zoom_level)
        screen_h = int(w_height * zoom_level)
        
        # Only draw if it's actually visible on the screen (Optional Optimization)
        if (screen_x + screen_w > 0 and screen_x < WIDTH and 
            screen_y + screen_h > 0 and screen_y < HEIGHT):
            pygame.draw.rect(screen, color, (screen_x, screen_y, screen_w, screen_h))

    pygame.display.flip()
    clock.tick(60)