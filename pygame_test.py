import pygame
import sys

# 1. Initialize Pygame and the display window
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Text in a Rectangle Example")

# 2. Define the target background rectangle (X, Y, Width, Height)
button_rect = pygame.Rect(300, 250, 200, 80)

# 3. Create the font object (None uses default system font)
# Define it outside the game loop to avoid performance lag
font = pygame.font.Font(None, 36)

# 4. Render the text surface (Text, Anti-aliasing, Text Color)
text_surface = font.render("Click Me", True, (255, 255, 255))

# 5. Get the text's bounding box and center it inside the background box
text_rect = text_surface.get_rect()
text_rect.center = button_rect.center

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear the screen
    screen.fill((40, 40, 40))

    # 6. DRAWING STEP: Draw the rectangle first, then layer the text on top
    pygame.draw.rect(screen, (0, 128, 255), button_rect)  # Blue rectangle
    screen.blit(text_surface, text_rect)                  # White text

    # Update display
    pygame.display.flip()
