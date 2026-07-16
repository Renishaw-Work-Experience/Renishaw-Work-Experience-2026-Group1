#-------------------------------- 2D Retro Car Game ---------------------------------#

#-------- 1. Importing Modules --------#

from cmath import rect
import pygame
import pygame.display

import sys
import os
import random

#-------- 2. Initialising Pygame --------#

pygame.init()
pygame.display.set_caption("Hello Pygame")

#-------- 3. Functions --------#

def load_image(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    return None


def create_player_surface():
    surface = pygame.Surface((40, 70), pygame.SRCALPHA)
    pygame.draw.rect(surface, (220, 40, 40), (8, 8, 24, 42))
    pygame.draw.rect(surface, (255, 255, 255), (10, 10, 20, 18))
    pygame.draw.rect(surface, (30, 30, 30), (10, 32, 20, 10))
    return surface

def draw_start_screen(surface):
    surface.blit(START_SCREEN_BACKGROUND, (0, -350))
    
    title = FONT_SMALL.render("Racing Game", True, (255, 255, 255))
    surface.blit(title, (245, 150))

    start_text = FONT_SMALL.render("START", True, (0, 0, 139))
    surface.blit(start_text, (275, 215))

    settings_text = FONT_SMALL.render("SETTINGS", True, (255, 0, 0))
    surface.blit(settings_text, (255, 295))

    pygame.draw.rect(surface, (0, 0, 139), START_BUTTON, 4)
    pygame.draw.rect(surface, (255, 0, 0), SETTINGS_BUTTON, 4)


def draw_settings_screen(surface):
    surface.fill((0, 0, 0))

    title = FONT_SMALL.render("Settings", True, (255, 255, 255))
    surface.blit(title, (155, 50))

    placeholder = FONT_SMALL.render("(coming soon)", True, (150, 150, 150))
    surface.blit(placeholder, (130, 110))

def trim_image(surface, bg_color=None):
    """
    Trims blank edges from a Pygame surface.
    - If bg_color is None, it will use transparency (alpha) to detect edges.
    - If bg_color is given (RGB tuple), it will trim that color.
    """
    surface = surface.copy()

    if bg_color is None:
        mask = pygame.mask.from_surface(surface, 1)
    else:
        mask = pygame.mask.from_threshold(surface, bg_color, (1, 1, 1, 255))

    rects = mask.get_bounding_rects()
    if rects:
        rect = rects[0]
        return surface.subsurface(rect).copy()

    return surface.copy()

#-------- 4. Constant Variables --------#

SCREEN = pygame.display.set_mode((600, 600)) # The actual pygame surface. Only reassigned when we resize the window on a screen change — never every frame.
CLOCK = pygame.time.Clock()
FPS = 60
LIVES = [3,3]  # lives for player 1 and player 2
IMMUNITY = [60, 60]  # frames of immunity after a collision
SCORE = [0,0]  # score for player 1 and player 2
CURRENT_SCREEN = 0
FONT_LARGE = pygame.font.Font(None, 72)
FONT_MEDIUM = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 28)
# Speeds / spawn rates
SPAWN_EVERY       = 60      # spawn one pothole every 60 frames (~1 second)
SPAWN_EVERY_COINS = 90      # spawn one coin every 90 frames (~1.5 seconds)
SPAWN_EVERY_ROCKS = 120     # spawn one rock every 120 frames (~2 seconds)
COIN_SPEED        = 5       # px/frame — how fast coins fall
OBSTACLE_SPEED    = 5       # px/frame — how fast rocks & potholes fall
PLAYER_1_CAR = load_image("player_1car.png.png").convert_alpha() or create_player_surface()
PLAYER_1_CAR = trim_image(PLAYER_1_CAR)  # Ensure the car is 40x70 pixels
PLAYER_2_CAR = load_image("player2_car.png.png").convert_alpha() or create_player_surface()
PLAYER_2_CAR = trim_image(PLAYER_2_CAR)  # Ensure the car is 40x70 pixels
START_SCREEN_BACKGROUND = load_image("start_screen_background.png.jpg").convert_alpha() or pygame.Surface((600, 600))
RACING_BACKGROUND = load_image("racing_background.png.png").convert_alpha() or pygame.Surface((600, 600))
CAR_FLASHING = load_image("car_flashing.png.png").convert_alpha() or pygame.Surface((600, 600))
POTHOLE_IMAGE = load_image('pothole.png')
START_BUTTON = pygame.Rect(255, 200, 100, 50) # order of numbers is x, y, width, height
SETTINGS_BUTTON = pygame.Rect(230, 280, 150, 50) # order of numbers is x, y, width, height
running = True

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

# State variable (NOT the pygame surface) — 0 = start, 1 = game, 2 = settings
# this was why it was failing as it was being reset to 0 every frame, so the game screen would never be drawn
# so thats why big issue :(


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
        self.rect.y += OBSTACLE_SPEED             # Move the rock down
        if self.rect.top > screen.get_height():   # Throw it away once it leaves the screen
            self.kill()

class Pothole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = POTHOLE_IMAGE
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += OBSTACLE_SPEED             # Move the pothole down
        if self.rect.top > screen.get_height():   # Throw it away once it leaves the screen
            self.kill()


COINS_LIST       = pygame.sprite.Group()
OBSTACLES_LIST = pygame.sprite.Group()
SPAWN_TIMER = 0
SPAWN_EVERY = 60                                  # spawn one pothole every 60 frames (~1 second)
spawn_timer_coins = 0
spawn_timer_rocks = 0

# ---- Player + road (merged from Car Movement.py) --------------------------
# Road geometry: the grey strip is centred in the 500-wide game window.
GAME_WIDTH   = 500
GAME_HEIGHT  = 600
ROAD_WIDTH   = 360
ROAD_LEFT    = (GAME_WIDTH - ROAD_WIDTH) // 2   # x where the road starts (70)
ROAD_RIGHT   = ROAD_LEFT + ROAD_WIDTH           # x where the road ends   (430)
PLAYER_SPEED = 4                                # pixels per frame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, player_num, colour):
        super().__init__()
        self.image = PLAYER_1_CAR                               # Player 1 Car
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self, keys):
        if (keys[pygame.K_a] and self.player_num == 1) or (keys[pygame.K_LEFT] and self.player_num == 2):
            if self.rect.x > ROAD_LEFT:
                self.rect.x -= PLAYER_SPEED
        if (keys[pygame.K_d] and self.player_num == 1) or (keys[pygame.K_RIGHT] and self.player_num == 2):
            if self.rect.x < ROAD_RIGHT - self.rect.width:
                self.rect.x += PLAYER_SPEED
        if (keys[pygame.K_w] and self.player_num == 1) or (keys[pygame.K_UP] and self.player_num == 2):
            if self.rect.y > 0:
                self.rect.y -= PLAYER_SPEED
        if (keys[pygame.K_s] and self.player_num == 1) or (keys[pygame.K_DOWN] and self.player_num == 2):
            if self.rect.y < GAME_HEIGHT - self.rect.height:
                self.rect.y += PLAYER_SPEED


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ROAD_WIDTH, GAME_HEIGHT))
        self.image.fill((50, 50, 50))                      # dark grey road
        self.rect = self.image.get_rect(topleft=(ROAD_LEFT, 0))


player1 = Player(200, 500, 1, (255, 0, 0))  # Red car for player 1
player2 = Player(300, 500, 2, (0, 0, 255))  # Blue car for player 2
player_group = pygame.sprite.Group(player1, player2)
bg = Background()


# Buttons at MODULE scope so both the drawing function and the event
# handler can see them.
start_button = pygame.Rect(150, 100, 100, 50)
settings_button = pygame.Rect(127, 180, 150, 50)


def draw_start_screen(surface):
    surface.fill((0, 0, 0))

    title = FONT_SMALL.render("Racing Game", True, (255, 255, 255))
    surface.blit(title, (135, 50))

    start_text = FONT_SMALL.render("START", True, (100, 200, 200))
    surface.blit(start_text, (170, 115))

    settings_text = FONT_SMALL.render("SETTINGS", True, (255, 0, 0))
    surface.blit(settings_text, (150, 195))

    pygame.draw.rect(surface, (100, 200, 200), start_button, 4)
    pygame.draw.rect(surface, (255, 0, 0), settings_button, 4)


def draw_settings_screen(surface):
    surface.fill((0, 0, 0))

    title = FONT_SMALL.render("Settings", True, (255, 255, 255))
    surface.blit(title, (155, 50))

    placeholder = FONT_SMALL.render("(coming soon)", True, (150, 150, 150))
    surface.blit(placeholder, (130, 110))


# Game loop
while running:
    clock.tick(FPS)

    # ONE event loop — pygame.event.get() drains the queue, so calling it twice
    # per frame silently eats the events (which is why the buttons weren't working).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False

        # Only react to clicks while on the start screen.
        if CURRENT_SCREEN == 0 and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if START_BUTTON.collidepoint(mouse_pos):
                print("Start button clicked!")
                CURRENT_SCREEN = 1
            elif SETTINGS_BUTTON.collidepoint(mouse_pos):
                print("Settings button clicked!")
                CURRENT_SCREEN = 2                             # go to settings

    # Draw + update per state
    if CURRENT_SCREEN == 0:
        draw_start_screen(SCREEN)

    elif CURRENT_SCREEN == 1:
        # Update the player from held keys (continuous movement, once per frame).
        keys = pygame.key.get_pressed()
        if LIVES[0] > 0:
            player1.update(keys)
        if LIVES[1] > 0:
            player2.update(keys)

        # Spawn a new pothole every SPAWN_EVERY frames.
        SPAWN_TIMER += 1
        if SPAWN_TIMER >= SPAWN_EVERY:
            SPAWN_TIMER = 0
            x = random.randint(ROAD_LEFT, ROAD_RIGHT - POTHOLE_IMAGE.get_width())
            OBSTACLES_LIST.add(Pothole(x, 0))

        OBSTACLES_LIST.update()

        # Draw: green surround, then the road, then obstacles, then the player on top.
        screen.fill((100, 255, 100))                       # grass
        screen.blit(bg.image, bg.rect)                     # road
        OBSTACLES_LIST.draw(screen)                        # potholes
        screen.blit(player.image, player.rect)             # car

        if (player.rect.colliderect(OBSTACLES_LIST.sprites()[0].rect) if OBSTACLES_LIST else False) and IMMUNITY == 0:
            print("Collision detected!")
            LIVES -= 1
            IMMUNITY = 60  # frames of immunity after a collision
            if LIVES <= 0:
                print("Game Over!")
                CURRENT_SCREEN = 0
                for obsticles in OBSTACLES_LIST:
                    OBSTACLES_LIST.remove(obsticles)
                screen = pygame.display.set_mode((400, 300))   # resize back to start screen
                LIVES = 3
                SCORE = 0
                player.rect.topleft = (200, 500)  # Reset player position
        
        if IMMUNITY > 0:
            IMMUNITY -= 1
            # Draw a visual indicator for immunity (e.g., a flashing effect)
            if IMMUNITY % 10 < 5:  # Flash every 5 frames
                pygame.draw.rect(screen, (255, 255, 0), player.rect, 3)  # Yellow border around the player
        
        SCORE += 1  # Increment score every frame
            
        lives_text = FONT_SMALL.render(f"Lives: {LIVES}", True, (255, 0, 0))
        screen.blit(lives_text, (10, 10))
        
        
        score_text = FONT_SMALL.render(f"Score: {SCORE}", True, (255, 255, 255))
        screen.blit(score_text, (10, 40))

    elif CURRENT_SCREEN == 2:
        draw_settings_screen(SCREEN)

    pygame.display.flip()

pygame.quit()
sys.exit()