import pygame
import sys

# Initialize Pygame
pygame.init()

# State variable (NOT the pygame surface) — 0 = start, 1 = game, 2 = settings
#this was why it was failing as it was being reset to 0 every frame, so the game screen would never be drawn
# so thats why big issue :(
current_screen = 0

clock = pygame.time.Clock()
FPS = 60

# The actual pygame surface. Only reassigned when we resize the window on
# a screen change — never every frame.
screen = pygame.display.set_mode((400, 300))

font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 28)

# Buttons at MODULE scope so both the drawing function and the event
# handler can see them.
start_button = pygame.Rect(150, 100, 100, 50)
settings_button = pygame.Rect(127, 180, 150, 50)


def draw_start_screen(surface):
    surface.fill((0, 0, 0))

    title = font_small.render("Racing Game", True, (255, 255, 255))
    surface.blit(title, (135, 50))

    start_text = font_small.render("START", True, (100, 200, 200))
    surface.blit(start_text, (170, 115))

    settings_text = font_small.render("SETTINGS", True, (255, 0, 0))
    surface.blit(settings_text, (150, 195))

    pygame.draw.rect(surface, (100, 200, 200), start_button, 4)
    pygame.draw.rect(surface, (255, 0, 0), settings_button, 4)


def draw_settings_screen(surface):
    surface.fill((0, 0, 0))

    title = font_small.render("Settings", True, (255, 255, 255))
    surface.blit(title, (155, 50))

    placeholder = font_small.render("(coming soon)", True, (150, 150, 150))
    surface.blit(placeholder, (130, 110))


# Game loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Only react to clicks while on the start screen.
        if current_screen == 0 and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if start_button.collidepoint(mouse_pos):
                print("Start button clicked!")
                screen = pygame.display.set_mode((500, 600))   # resize once, not per frame
                current_screen = 1
            elif settings_button.collidepoint(mouse_pos):
                print("Settings button clicked!")
                current_screen = 2                             # go to settings

    # Draw whichever screen we're on.
    if current_screen == 0:
        draw_start_screen(screen)
    elif current_screen == 1:
        screen.fill((0, 0, 0))
        # ... game drawing goes here ...
    elif current_screen == 2:
        draw_settings_screen(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

