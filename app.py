import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Hello Pygame")

# The actual pygame surface. Only reassigned when we resize the window on
# a screen change — never every frame.
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()
FPS = 60

# State variable (NOT the pygame surface) — 0 = start, 1 = game, 2 = settings
# this was why it was failing as it was being reset to 0 every frame, so the game screen would never be drawn
# so thats why big issue :(
current_screen = 0

font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 28)

# Try to load the pothole PNG; fall back to a drawn shape if the file is missing.
if os.path.exists('pothole.png'):
    pothole_image = pygame.image.load('pothole.png').convert_alpha()
else:
    pothole_image = pygame.Surface((60, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(pothole_image, (60, 60, 60), pothole_image.get_rect())
    pygame.draw.ellipse(pothole_image, (30, 30, 30), pothole_image.get_rect(), 3)


class Pothole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pothole_image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.y += 5                          # Move the pothole down by 5 pixels
        if self.rect.top > screen.get_height():   # Throw it away once it leaves the screen
            self.kill()


obstacles_list = pygame.sprite.Group()
spawn_timer = 0
SPAWN_EVERY = 60                                  # spawn one pothole every 60 frames (~1 second)

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

    # ONE event loop — pygame.event.get() drains the queue, so calling it twice
    # per frame silently eats the events (which is why the buttons weren't working).
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

    # Draw + update per state
    if current_screen == 0:
        draw_start_screen(screen)

    elif current_screen == 1:
        # Spawn a new pothole every SPAWN_EVERY frames.
        spawn_timer += 1
        if spawn_timer >= SPAWN_EVERY:
            spawn_timer = 0
            x = random.randint(0, screen.get_width() - pothole_image.get_width())
            obstacles_list.add(Pothole(x, 0))

        obstacles_list.update()

        screen.fill((80, 80, 80))
        obstacles_list.draw(screen)

    elif current_screen == 2:
        draw_settings_screen(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

