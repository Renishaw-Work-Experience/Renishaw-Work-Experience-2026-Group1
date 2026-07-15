import pygame
import pygame.display

import sys
import os
import random

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Hello Pygame")

# The actual pygame surface. Only reassigned when we resize the window on
# a screen change — never every frame.
# NOTE: this MUST come before any pygame.image.load(...).convert_alpha() call,
# because convert_alpha() needs an active display surface to exist.
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()
FPS = 60


def _coin_placeholder():
    # Small yellow circle used when a mario-coins-N.png file isn't on disk.
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 215, 0), (15, 15), 12)
    return surf


if os.path.exists('mario-coins-1.png'):
    gif_1 = pygame.image.load('mario-coins-1.png').convert_alpha()
else:
    gif_1 = _coin_placeholder()
if os.path.exists('mario-coins-2.png'):
    gif_2 = pygame.image.load('mario-coins-2.png').convert_alpha()
else:
    gif_2 = _coin_placeholder()
if os.path.exists('mario-coins-3.png'):
    gif_3 = pygame.image.load('mario-coins-3.png').convert_alpha()
else:
    gif_3 = _coin_placeholder()
if os.path.exists('mario-coins-4.png'):
    gif_4 = pygame.image.load('mario-coins-4.png').convert_alpha()
else:
    gif_4 = _coin_placeholder()
if os.path.exists('mario-coins-5.png'):
    gif_5 = pygame.image.load('mario-coins-5.png').convert_alpha()
else:
    gif_5 = _coin_placeholder()
if os.path.exists('mario-coins-6.png'):
    gif_6 = pygame.image.load('mario-coins-6.png').convert_alpha()
else:
    gif_6 = _coin_placeholder()
if os.path.exists('mario-coins-7.png'):
    gif_7 = pygame.image.load('mario-coins-7.png').convert_alpha()
else:
    gif_7 = _coin_placeholder()
if os.path.exists('mario-coins-8.png'):
    gif_8 = pygame.image.load('mario-coins-8.png').convert_alpha()
else:
    gif_8 = _coin_placeholder()
coin_gif = [gif_1, gif_2, gif_3, gif_4, gif_5, gif_6, gif_7, gif_8]


coins_list = pygame.sprite.Group()
obstacles_list = pygame.sprite.Group()

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

if os.path.exists('rock.png'):
    rock_image = pygame.image.load('rock.png').convert_alpha()
else:
    rock_image = pygame.Surface((60, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(rock_image, (60, 60, 60), rock_image.get_rect())
    pygame.draw.ellipse(rock_image, (30, 30, 30), rock_image.get_rect(), 3)

if os.path.exists('coin.png'):
    coin_image = pygame.image.load('coin.png').convert_alpha()
else:
    coin_image = pygame.Surface((60, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(coin_image, (60, 60, 60), coin_image.get_rect())
    pygame.draw.ellipse(coin_image, (30, 30, 30), coin_image.get_rect(), 3)


class Coin(pygame.sprite.Sprite):
    # Advance one animation frame every ANIMATION_INTERVAL game ticks.
    # At FPS=60 and interval=6 that's ~10 fps for the coin spin.
    ANIMATION_INTERVAL = 6

    def __init__(self, x, y):
        super().__init__()
        self.frame_index = 0
        self.frame_timer = 0
        self.image = coin_gif[0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        # Tick the per-sprite animation timer and swap frames when it fires.
        self.frame_timer += 1
        if self.frame_timer >= Coin.ANIMATION_INTERVAL:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(coin_gif)
            # Preserve the centre so different-sized frames don't jump around.
            old_center = self.rect.center
            self.image = coin_gif[self.frame_index]
            self.rect = self.image.get_rect(center=old_center)

        self.rect.y += COIN_SPEED                 # Move the coin down
        if self.rect.top > screen.get_height():   # Throw it away once it leaves the screen
            self.kill()


class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = rock_image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.y += OBSTACLE_SPEED                          # Move the rock down by 5 pixels
        if self.rect.top > screen.get_height():   # Throw it away once it leaves the screen
            self.kill()


class Pothole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pothole_image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.y += OBSTACLE_SPEED                          # Move the pothole down by 5 pixels
        if self.rect.top > screen.get_height():   # Throw it away once it leaves the screen
            self.kill()


spawn_timer_rocks = 0
spawn_timer_coins = 0
spawn_timer = 0

SPAWN_EVERY = 20               # spawn one pothole every 20 frames
SPAWN_EVERY_COINS = 30         # spawn one coin every 30 frames
SPAWN_EVERY_ROCKS = 40         # spawn one rock every 40 frames
COIN_SPEED = 5                 # speed at which coins fall
OBSTACLE_SPEED = 10             # speed at which obstacles fall

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
            #x = random.randint(0, screen.get_width() - coin_image.get_width())
            x_1 = random.randint(0, screen.get_width() - pothole_image.get_width())
            #coins_list.add(Coin(x, 0))
            obstacles_list.add(Pothole(x_1, 0))

        spawn_timer_coins += 1
        if spawn_timer_coins >= SPAWN_EVERY_COINS:
            spawn_timer_coins = 0
            x = random.randint(0, screen.get_width() - coin_image.get_width())
            #x_1 = random.randint(0, screen.get_width() - pothole_image.get_width())
            coins_list.add(Coin(x, 0))
            #obstacles_list.add(Pothole(x_1, 0))

        spawn_timer_rocks += 1
        if spawn_timer_rocks >= SPAWN_EVERY_ROCKS:
            spawn_timer_rocks = 0
            x = random.randint(0, screen.get_width() - rock_image.get_width())
            #x_1 = random.randint(0, screen.get_width() - pothole_image.get_width())
            obstacles_list.add(Rock(x, 0))
            #obstacles_list.add(Pothole(x_1, 0))

        coins_list.update()
        obstacles_list.update()

        screen.fill((80, 80, 80))
        obstacles_list.draw(screen)
        coins_list.draw(screen)

    elif current_screen == 2:
        draw_settings_screen(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()