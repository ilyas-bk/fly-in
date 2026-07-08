import pygame
import sys

# Initialize pygame
pygame.init()

# 1. Create the game window display surface
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Display Image Example")

# 2. Load and optimize the image surface
# Use .convert_alpha() for transparent PNGs, or .convert() for JPGs
my_image = pygame.image.load("drone.png").convert_alpha()

# Main game loop
running = True
while running:
    # Handle window close events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    my_image = pygame.transform.scale(my_image, (50, 50))
    # Clear the screen with a background color (RGB tuple)
    screen.fill((255, 255, 255))

    # 3. Blit (draw) the image onto the screen at X=100, Y=150
    screen.blit(my_image, (100, 150))

    # 4. Flip the display to show the changes
    pygame.display.flip()
    
# Clean up and close
pygame.quit()
sys.exit()
