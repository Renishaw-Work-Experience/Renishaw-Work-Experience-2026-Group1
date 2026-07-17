"""
file2.py — 2-player racing game with configurable settings.

Merges the working 2-player game code from file1.py (mask collision,
PNG car assets, scrolling road, coin pickups, rock/pothole obstacles,
player push) with a full 600x600 settings screen:

  * Difficulty:    easy / medium / hard / impossible
  * Car speed:     50 CC / 100 CC / 150 CC / 200 CC
  * Players:       1 or 2

Defaults are pre-highlighted on first open of the settings screen:
    1 Player,  Easy,  50 CC.

In 1-player mode player1 responds to both WASD and arrow keys.
"""

import pygame
import sys
import os
import random


# ---------------------------------------------------------------------------
# Pygame init + display
# ---------------------------------------------------------------------------

pygame.init()
pygame.display.set_caption("Racing Game")

# Window sizes per screen. All three screens are 600x600 so the start
# screen (copied from file1.py) has room for the title, buttons and
# background image.
START_SIZE    = (600, 600)
GAME_SIZE     = (600, 600)
SETTINGS_SIZE = (600, 600)

# The actual pygame surface. Only reassigned when we resize the window on
# a screen change — never every frame.
# NOTE: this MUST come before any pygame.image.load(...).convert_alpha()
# call, because convert_alpha() needs an active display surface.
screen = pygame.display.set_mode(START_SIZE)
clock  = pygame.time.Clock()

font_large  = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small  = pygame.font.Font(None, 28)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FPS = 60

# Screen-state IDs (values of `current_screen`).
SCREEN_START    = 0
SCREEN_GAME     = 1
SCREEN_SETTINGS = 2

# Game window / road geometry (must match GAME_SIZE).
GAME_WIDTH, GAME_HEIGHT = GAME_SIZE
ROAD_WIDTH = 420
ROAD_LEFT  = (GAME_WIDTH - ROAD_WIDTH) // 2   #  90 — x where the road starts
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH           # 510 — x where the road ends

# Player start positions (used at boot and by reset_game()).
PLAYER1_START = (200, 500)
PLAYER2_START = (350, 500)

# Movement speeds (pixels per frame). PLAYER_SPEED gets rebound by the
# car-speed buttons in the settings screen.
PLAYER_SPEED   = 4
COIN_SPEED     = 5
OBSTACLE_SPEED = 5
PUSH_SPEED     = 5

# Spawn rates (frames — at FPS=60, 60 frames ≈ 1 second). SPAWN_EVERY is
# rebound by the difficulty buttons.
SPAWN_EVERY       = 60
SPAWN_EVERY_COINS = 90
SPAWN_EVERY_ROCKS = 120

# Scoring & lives.
STARTING_LIVES   = 3
IMMUNITY_FRAMES  = 60
COIN_SCORE_BONUS = 500


# ---------------------------------------------------------------------------
# Global state (per-player state uses index 0 = player1, index 1 = player2)
# ---------------------------------------------------------------------------

lives    = [STARTING_LIVES,  STARTING_LIVES]
immunity = [IMMUNITY_FRAMES, IMMUNITY_FRAMES]
score    = [0, 0]

spawn_timer       = 0
spawn_timer_coins = 0
spawn_timer_rocks = 0

# State variable (NOT the pygame surface).
# this was why it was failing as it was being reset to 0 every frame, so the
# game screen would never be drawn — so that's why big issue :(
current_screen = SCREEN_START


# ---------------------------------------------------------------------------
# Difficulty / car-speed / player-count selection.
#
# The defaults set here are what gets highlighted on the settings screen on
# first open:  1 player, Easy, 50 CC (slowest).
# ---------------------------------------------------------------------------

DIFFICULTY_OBSTACLE_SPEED = {'easy': 5, 'medium': 6, 'hard':  7, 'impossible':  9}
DIFFICULTY_SPAWN_EVERY    = {'easy': 60, 'medium': 50, 'hard': 40, 'impossible': 10}
SPEED_OBSTACLE_BONUS      = {'speed1': 0, 'speed2': 1, 'speed3': 2, 'speed4': 3}
SPEED_PLAYER_SPEED        = {'speed1': 4, 'speed2': 6, 'speed3': 8, 'speed4': 10}

selected_difficulty = 'easy'      # default — highlighted on first settings open
selected_speed      = 'speed1'    # default — highlighted on first settings open
selected_players    = 1           # default — highlighted on first settings open


def recompute_obstacle_speed():
    """Set OBSTACLE_SPEED from the currently selected difficulty and car speed."""
    global OBSTACLE_SPEED
    base  = DIFFICULTY_OBSTACLE_SPEED.get(selected_difficulty, 5)
    bonus = SPEED_OBSTACLE_BONUS.get(selected_speed, 0)
    OBSTACLE_SPEED = base + bonus


# Sync the derived tuning values with the defaults so the very first game
# respects "1 player / Easy / 50 CC" without needing to open settings.
recompute_obstacle_speed()
SPAWN_EVERY  = DIFFICULTY_SPAWN_EVERY[selected_difficulty]
PLAYER_SPEED = SPEED_PLAYER_SPEED[selected_speed]


# ---------------------------------------------------------------------------
# Drifting safe-corridor spawn constraint (ported from main.py).
#
# A vertical stripe of the road that never gets a pothole or rock spawned
# in it, so the players always have at least one clear path. Think of it
# as an invisible car sliding sideways along the road — obstacles never
# spawn where it is right now. The corridor drifts smoothly toward a
# random target x, then picks a new target when it arrives.
#
# 120 px is wide enough to fit two 50-px cars side by side in 2P mode
# (with a little slack) and gives a comfortable safe path in 1P mode.
# Coins are NOT restricted — they can spawn inside the corridor so there
# is still a risk/reward decision when collecting them.
# ---------------------------------------------------------------------------

CORRIDOR_WIDTH       = 120     # width of the always-clear stripe (px)
CORRIDOR_DRIFT_SPEED = 2.5     # px the corridor slides per frame (must be < PLAYER_SPEED)
corridor_center_x = (ROAD_LEFT + ROAD_RIGHT) / 2   # start dead-centre
corridor_target_x = corridor_center_x              # nothing to drift toward yet


def random_x_avoiding_corridor(obstacle_width):
    """Pick a random x on the road that's outside the current safe corridor."""
    corridor_left  = corridor_center_x - CORRIDOR_WIDTH / 2
    corridor_right = corridor_center_x + CORRIDOR_WIDTH / 2

    left_min,  left_max  = ROAD_LEFT,           int(corridor_left  - obstacle_width)
    right_min, right_max = int(corridor_right), ROAD_RIGHT - obstacle_width

    left_size  = max(0, left_max  - left_min)
    right_size = max(0, right_max - right_min)

    if left_size <= 0 and right_size <= 0:
        # Corridor covers the whole road — shouldn't happen with sensible params.
        return random.randint(ROAD_LEFT, ROAD_RIGHT - obstacle_width)

    # Weighted pick: prefer whichever side has more room to spawn on.
    if random.random() < left_size / (left_size + right_size):
        return random.randint(left_min, left_max)
    return random.randint(right_min, right_max)


# ---------------------------------------------------------------------------
# Asset-loading helpers (with safe fallbacks so the game still runs when
# a PNG isn't present on disk).
# ---------------------------------------------------------------------------

def load_image(filename):
    """Return the image at ``filename`` as a display-ready surface, or None."""
    path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    return None


def load_or_fallback(filename, fallback):
    """Load ``filename`` if present, otherwise return ``fallback``."""
    img = load_image(filename)
    return img if img is not None else fallback


def trim_image(surface):
    """Crop transparent padding around a surface."""
    if surface is None:
        return surface
    rect = surface.get_bounding_rect()
    if rect.width == 0 or rect.height == 0:
        return surface
    trimmed = pygame.Surface(rect.size, pygame.SRCALPHA)
    trimmed.blit(surface, (0, 0), rect)
    return trimmed


def create_player_surface(colour):
    """Fallback 50x80 car surface used when a player PNG is missing."""
    surface = pygame.Surface((50, 80), pygame.SRCALPHA)
    pygame.draw.rect(surface, colour,          (8,  8, 34, 64))   # body
    pygame.draw.rect(surface, (255, 255, 255), (12, 14, 26, 22))  # windshield
    pygame.draw.rect(surface, (30, 30, 30),    (12, 46, 26, 12))  # bumper
    return surface


def _coin_placeholder():
    """Small yellow circle used when a mario-coins-N.png file isn't on disk."""
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surface, (255, 215, 0), (15, 15), 12)
    return surface


def _ellipse_placeholder():
    """Grey ellipse used when pothole.png / rock.png / coin.png is missing."""
    surface = pygame.Surface((60, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, (60, 60, 60), surface.get_rect())
    pygame.draw.ellipse(surface, (30, 30, 30), surface.get_rect(), 3)
    return surface


# ---------------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------------

# Mario coin-spin animation frames 1..8.
coin_gif = [
    load_or_fallback(f"mario-coins-{i}.png", _coin_placeholder())
    for i in range(1, 9)
]

# Static obstacle images.
pothole_image = load_or_fallback("pothole.png", _ellipse_placeholder())
rock_image    = load_or_fallback("rock.png",    _ellipse_placeholder())
coin_image    = load_or_fallback("coin.png",    _ellipse_placeholder())

# Car / background images (with drawn-shape fallbacks).
PLAYER_1_CAR = trim_image(load_or_fallback("player_1car.png.png",
                                           create_player_surface((220, 40, 40))))   # red
PLAYER_2_CAR = trim_image(load_or_fallback("player2_car.png.png",
                                           create_player_surface((40, 40, 220))))   # blue
START_SCREEN_BACKGROUND = load_or_fallback("start_screen_background.png.jpg",
                                           pygame.Surface((600, 600)))
RACING_BACKGROUND       = load_or_fallback("racing_background.png.png",
                                           pygame.Surface((600, 600)))
CAR_FLASHING            = load_or_fallback("car_flashing.png.png",
                                           pygame.Surface((60, 90), pygame.SRCALPHA))

# Home-icon asset used on the settings screen (replaces the old "Back"
# button). Load once at module scope; fall back to a hand-drawn stylised
# house so the game still runs without the PNG on disk.
if os.path.exists('house.png'):
    home_icon = pygame.image.load('house.png').convert_alpha()
elif os.path.exists('home_icon.png'):
    home_icon = pygame.image.load('home_icon.png').convert_alpha()
elif os.path.exists('home icon2.png'):
    home_icon = pygame.image.load('home icon2.png').convert_alpha()
else:
    home_icon = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.polygon(home_icon, (200, 60, 60),   [(50, 10), (10, 50), (90, 50)])   # roof
    pygame.draw.rect(home_icon,    (220, 220, 220), pygame.Rect(20, 50, 60, 45))       # body
    pygame.draw.rect(home_icon,    (100, 60, 30),   pygame.Rect(42, 65, 16, 30))       # door
# Strip any transparent padding around the imported PNG so the visible
# house fills its whole surface — without this, the icon looks off-centre
# because the invisible padding shifts it inside its bounding box.
home_icon = trim_image(home_icon)
home_icon = pygame.transform.scale(home_icon, (60, 60))


# ---------------------------------------------------------------------------
# Sprite classes
# ---------------------------------------------------------------------------

class Coin(pygame.sprite.Sprite):
    """Falling coin with per-sprite animation (mario spin cycle)."""

    # Advance one animation frame every ANIMATION_INTERVAL game ticks.
    # At FPS=60 and interval=6 that's ~10 fps for the coin spin.
    ANIMATION_INTERVAL = 6

    def __init__(self, x, y):
        super().__init__()
        self.frame_index = 0
        self.frame_timer = 0
        self.image = coin_gif[0]
        self.rect  = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.frame_timer += 1
        if self.frame_timer >= Coin.ANIMATION_INTERVAL:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(coin_gif)
            # Preserve the centre so different-sized frames don't jump around.
            old_center = self.rect.center
            self.image = coin_gif[self.frame_index]
            self.rect  = self.image.get_rect(center=old_center)
        self.rect.y += COIN_SPEED
        if self.rect.top > screen.get_height():
            self.kill()


class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = rock_image
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.mask  = pygame.mask.from_surface(self.image)   # pixel-perfect collision

    def update(self):
        self.rect.y += OBSTACLE_SPEED
        if self.rect.top > screen.get_height():
            self.kill()


class Pothole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pothole_image
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.mask  = pygame.mask.from_surface(self.image)   # pixel-perfect collision

    def update(self):
        self.rect.y += OBSTACLE_SPEED
        if self.rect.top > screen.get_height():
            self.kill()


class Player(pygame.sprite.Sprite):
    """Two-player controller (WASD for P1, arrow keys for P2).

    In 1-player mode, player1 also responds to arrow keys so a solo player
    can use whichever key layout feels natural.
    """

    def __init__(self, x, y, player_num, image):
        super().__init__()
        self.player_num = player_num
        self.image = image
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.mask  = pygame.mask.from_surface(self.image)   # pixel-perfect collision

    def update(self, keys):
        if self.player_num == 1:
            # WASD always; arrow keys too when playing solo.
            solo = (selected_players == 1)
            left  = keys[pygame.K_a] or (solo and keys[pygame.K_LEFT])
            right = keys[pygame.K_d] or (solo and keys[pygame.K_RIGHT])
            up    = keys[pygame.K_w] or (solo and keys[pygame.K_UP])
            down  = keys[pygame.K_s] or (solo and keys[pygame.K_DOWN])
        else:
            # Player 2: arrow keys only (only used in 2-player mode).
            left  = keys[pygame.K_LEFT]
            right = keys[pygame.K_RIGHT]
            up    = keys[pygame.K_UP]
            down  = keys[pygame.K_DOWN]

        if left  and self.rect.x > ROAD_LEFT:
            self.rect.x -= PLAYER_SPEED
        if right and self.rect.x < ROAD_RIGHT - self.rect.width:
            self.rect.x += PLAYER_SPEED
        if up    and self.rect.y > 0:
            self.rect.y -= PLAYER_SPEED
        if down  and self.rect.y < GAME_HEIGHT - self.rect.height:
            self.rect.y += PLAYER_SPEED


class Background(pygame.sprite.Sprite):
    """Static grey road strip — fallback when RACING_BACKGROUND is missing."""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ROAD_WIDTH, GAME_HEIGHT))
        self.image.fill((50, 50, 50))                       # dark grey road
        self.rect  = self.image.get_rect(topleft=(ROAD_LEFT, 0))


# ---------------------------------------------------------------------------
# Sprite instances, groups, and UI rects
# ---------------------------------------------------------------------------

player1 = Player(*PLAYER1_START, 1, PLAYER_1_CAR)   # red car
player2 = Player(*PLAYER2_START, 2, PLAYER_2_CAR)   # blue car
player_group   = pygame.sprite.Group(player1, player2)
coins_list     = pygame.sprite.Group()
obstacles_list = pygame.sprite.Group()
bg = Background()

# Start-screen buttons (positioned for the 600x600 start window,
# matching file1.py so the outline sits behind the START / SETTINGS
# text).
start_button    = pygame.Rect(255, 200, 100, 50)
settings_button = pygame.Rect(230, 280, 150, 50)

# Settings-screen buttons (positioned for the 600x600 settings window).
easy_button       = pygame.Rect( 70, 130, 100, 50)
medium_button     = pygame.Rect(190, 130, 100, 50)
hard_button       = pygame.Rect(310, 130, 100, 50)
impossible_button = pygame.Rect(430, 130, 100, 50)

speed1_button = pygame.Rect( 70, 280, 100, 50)
speed2_button = pygame.Rect(190, 280, 100, 50)
speed3_button = pygame.Rect(310, 280, 100, 50)
speed4_button = pygame.Rect(430, 280, 100, 50)

one_player_button  = pygame.Rect(110, 430, 170, 50)
two_player_button  = pygame.Rect(320, 430, 170, 50)

# Home icon on the settings screen (top-left). Click this to go back to
# the start screen — replaces the old plain "Back" button. Size must
# match the scaled home_icon so the click zone lines up with the visible
# house.
home_icon_settings_rect = pygame.Rect(10, 10, 60, 60)


# ---------------------------------------------------------------------------
# Drawing functions
# ---------------------------------------------------------------------------

def draw_start_screen(surface):
    # Start screen copied from file1.py: background image (offset up by
    # 350 to show the interesting part) with title + START + SETTINGS
    # text sitting inside the corresponding button outlines.
    surface.blit(START_SCREEN_BACKGROUND, (0, -350))

    title         = font_small.render("Racing Game", True, (0, 0, 0))
    start_text    = font_small.render("START",       True, (0, 0, 139))
    settings_text = font_small.render("SETTINGS",    True, (255, 0, 0))

    surface.blit(title,         (245, 150))
    surface.blit(start_text,    (275, 215))
    surface.blit(settings_text, (255, 295))

    pygame.draw.rect(surface, (0, 0, 139), start_button,    4)
    pygame.draw.rect(surface, (255, 0, 0), settings_button, 4)


def draw_settings_screen(surface):
    surface.fill((0, 0, 0))

    # Title (centred at the top of the 600x600 settings window).
    title = font_medium.render("Settings", True, (255, 255, 255))
    surface.blit(title, (230, 25))

    # Home icon (top-left) — click to go back to the start screen.
    surface.blit(home_icon, home_icon_settings_rect.topleft)

    # ---- Difficulty section ----
    surface.blit(font_small.render("Difficulty", True, (255, 255, 255)), (60, 95))
    pygame.draw.line(surface, (255, 255, 255), (60, 118), (150, 118), 2)

    pygame.draw.rect(surface, (0, 255, 0),     easy_button)
    pygame.draw.rect(surface, (100, 200, 200), medium_button)
    pygame.draw.rect(surface, (0, 0, 255),     hard_button)
    pygame.draw.rect(surface, (255, 0, 0),     impossible_button)

    surface.blit(font_small.render("Easy",       True, (0, 255, 0)),     ( 90, 195))
    surface.blit(font_small.render("Medium",     True, (100, 200, 200)), (200, 195))
    surface.blit(font_small.render("Hard",       True, (0, 0, 255)),     (335, 195))
    surface.blit(font_small.render("Impossible", True, (255, 0, 0)),     (425, 195))

    # ---- Car-speed section ----
    surface.blit(font_small.render("Car speed", True, (255, 255, 255)), (60, 245))
    pygame.draw.line(surface, (255, 255, 255), (60, 268), (155, 268), 2)

    pygame.draw.rect(surface, (255, 255, 0),  speed1_button)
    pygame.draw.rect(surface, (255, 131, 15), speed2_button)
    pygame.draw.rect(surface, (183, 47, 71),  speed3_button)
    pygame.draw.rect(surface, (145, 0, 146),  speed4_button)

    surface.blit(font_small.render("50 CC",  True, (255, 255, 0)),  ( 78, 345))
    surface.blit(font_small.render("100 CC", True, (255, 131, 15)), (198, 345))
    surface.blit(font_small.render("150 CC", True, (183, 47, 71)),  (318, 345))
    surface.blit(font_small.render("200 CC", True, (145, 0, 146)),  (438, 345))

    # ---- Players section (bottom of the screen) ----
    surface.blit(font_small.render("Players", True, (255, 255, 255)), (60, 395))
    pygame.draw.line(surface, (255, 255, 255), (60, 418), (135, 418), 2)

    pygame.draw.rect(surface, (100, 200, 100), one_player_button)
    pygame.draw.rect(surface, (200, 100, 100), two_player_button)

    surface.blit(font_small.render("1 Player",  True, (100, 200, 100)), (140, 495))
    surface.blit(font_small.render("2 Players", True, (200, 100, 100)), (345, 495))

    # ---- Selected-button highlights (bright white outline). ----
    HIGHLIGHT_COLOUR = (255, 255, 255)
    HIGHLIGHT_WIDTH  = 5

    if   selected_difficulty == 'easy':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, easy_button,       HIGHLIGHT_WIDTH)
    elif selected_difficulty == 'medium':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, medium_button,     HIGHLIGHT_WIDTH)
    elif selected_difficulty == 'hard':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, hard_button,       HIGHLIGHT_WIDTH)
    elif selected_difficulty == 'impossible':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, impossible_button, HIGHLIGHT_WIDTH)

    if   selected_speed == 'speed1':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, speed1_button, HIGHLIGHT_WIDTH)
    elif selected_speed == 'speed2':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, speed2_button, HIGHLIGHT_WIDTH)
    elif selected_speed == 'speed3':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, speed3_button, HIGHLIGHT_WIDTH)
    elif selected_speed == 'speed4':
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, speed4_button, HIGHLIGHT_WIDTH)

    if   selected_players == 1:
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, one_player_button, HIGHLIGHT_WIDTH)
    elif selected_players == 2:
        pygame.draw.rect(surface, HIGHLIGHT_COLOUR, two_player_button, HIGHLIGHT_WIDTH)


# ---------------------------------------------------------------------------
# Game-flow helpers
# ---------------------------------------------------------------------------

def reset_game():
    """Reset all game state before a new game.

    In 1-player mode this also parks player2 off-screen and zeroes its
    lives so the "player2 active?" checks in the game loop naturally
    skip it.
    """
    global lives, immunity, score, spawn_timer, spawn_timer_coins, spawn_timer_rocks
    lives    = [STARTING_LIVES,  STARTING_LIVES]
    immunity = [IMMUNITY_FRAMES, IMMUNITY_FRAMES]
    score    = [0, 0]
    spawn_timer       = 0
    spawn_timer_coins = 0
    spawn_timer_rocks = 0
    for obstacle in list(obstacles_list):
        obstacles_list.remove(obstacle)
    for coin in list(coins_list):
        coins_list.remove(coin)
    player1.rect.topleft = PLAYER1_START
    player2.rect.topleft = PLAYER2_START
    if selected_players == 1:
        lives[1] = 0
        player2.rect.topleft = (1000, 1000)


def handle_player_collision(player_index, player_sprite):
    """Check obstacles vs one player; decrement lives and handle game over."""
    global current_screen
    if immunity[player_index] != 0:
        return
    for obstacle in obstacles_list:
        if pygame.sprite.collide_mask(player_sprite, obstacle):
            print(f"Player {player_index + 1} collision detected!")
            lives[player_index]    -= 1
            immunity[player_index]  = IMMUNITY_FRAMES
            obstacle.kill()                              # remove the obstacle that was hit

            # Game-over trigger differs between 1P and 2P modes.
            if selected_players == 1:
                game_over = lives[0] <= 0
            else:
                game_over = lives[0] <= 0 and lives[1] <= 0

            if game_over:
                print("Game Over!")
                current_screen = SCREEN_START
                reset_game()
            elif selected_players == 2 and lives[player_index] <= 0:
                print(f"Player {player_index + 1} has lost all lives!")
                player_sprite.rect.topleft = (1000, 1000)   # off-screen
            break


def handle_coin_collection(player_index, player_sprite):
    """Check coins vs one player; pick up (remove) each coin and award score.

    Uses rect collision (not mask) because the coin sprite's image swaps
    every animation frame, which would make a cached mask go out of sync.
    """
    for coin in coins_list:
        if player_sprite.rect.colliderect(coin.rect):
            coin.kill()
            score[player_index] += COIN_SCORE_BONUS
            print(f"Player {player_index + 1} collected a coin! (+{COIN_SCORE_BONUS})")


def handle_player_push():
    """Push the two players apart when they overlap (2P mode only)."""
    if selected_players != 2:
        return
    if lives[0] <= 0 or lives[1] <= 0:
        return
    if not player1.rect.colliderect(player2.rect):
        return

    # Vertical push
    if player1.rect.y > player2.rect.y:
        if player1.rect.y < screen.get_height() - player1.rect.height:
            player1.rect.y += PUSH_SPEED
        if player2.rect.y > 0:
            player2.rect.y -= PUSH_SPEED
    elif player1.rect.y < player2.rect.y:
        if player1.rect.y > 0:
            player1.rect.y -= PUSH_SPEED
        if player2.rect.y < screen.get_height() - player2.rect.height:
            player2.rect.y += PUSH_SPEED

    # Horizontal push
    if player1.rect.x > player2.rect.x:
        if player1.rect.x < ROAD_RIGHT - player1.rect.width:
            player1.rect.x += PUSH_SPEED
        if player2.rect.x > ROAD_LEFT:
            player2.rect.x -= PUSH_SPEED
    elif player1.rect.x < player2.rect.x:
        if player1.rect.x > ROAD_LEFT:
            player1.rect.x -= PUSH_SPEED
        if player2.rect.x < ROAD_RIGHT - player2.rect.width:
            player2.rect.x += PUSH_SPEED


# Apply the "1 player by default" state before the game loop starts,
# so player2 is already parked off-screen on first Start click.
reset_game()


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

running = True
while running:
    clock.tick(FPS)

    # ONE event loop — pygame.event.get() drains the queue, so calling it
    # twice per frame silently eats events (which is why the buttons
    # weren't working previously).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---- Start-screen clicks ----
        if current_screen == SCREEN_START and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if start_button.collidepoint(mouse_pos):
                print("Start button clicked!")
                reset_game()                                  # fresh game state
                screen = pygame.display.set_mode(GAME_SIZE)   # resize once
                current_screen = SCREEN_GAME
            elif settings_button.collidepoint(mouse_pos):
                print("Settings button clicked!")
                screen = pygame.display.set_mode(SETTINGS_SIZE)
                current_screen = SCREEN_SETTINGS

        # ---- Settings-screen clicks ----
        elif current_screen == SCREEN_SETTINGS and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if home_icon_settings_rect.collidepoint(mouse_pos):
                print("Home icon clicked!")
                screen = pygame.display.set_mode(START_SIZE)
                current_screen = SCREEN_START

            # Difficulty
            elif easy_button.collidepoint(mouse_pos):
                print("Easy button clicked!")
                selected_difficulty = 'easy'
                SPAWN_EVERY = DIFFICULTY_SPAWN_EVERY[selected_difficulty]
                recompute_obstacle_speed()
            elif medium_button.collidepoint(mouse_pos):
                print("Medium button clicked!")
                selected_difficulty = 'medium'
                SPAWN_EVERY = DIFFICULTY_SPAWN_EVERY[selected_difficulty]
                recompute_obstacle_speed()
            elif hard_button.collidepoint(mouse_pos):
                print("Hard button clicked!")
                selected_difficulty = 'hard'
                SPAWN_EVERY = DIFFICULTY_SPAWN_EVERY[selected_difficulty]
                recompute_obstacle_speed()
            elif impossible_button.collidepoint(mouse_pos):
                print("Impossible button clicked!")
                selected_difficulty = 'impossible'
                SPAWN_EVERY = DIFFICULTY_SPAWN_EVERY[selected_difficulty]
                recompute_obstacle_speed()

            # Car speed
            elif speed1_button.collidepoint(mouse_pos):
                print("50 CC selected!")
                selected_speed = 'speed1'
                PLAYER_SPEED = SPEED_PLAYER_SPEED[selected_speed]
                recompute_obstacle_speed()
            elif speed2_button.collidepoint(mouse_pos):
                print("100 CC selected!")
                selected_speed = 'speed2'
                PLAYER_SPEED = SPEED_PLAYER_SPEED[selected_speed]
                recompute_obstacle_speed()
            elif speed3_button.collidepoint(mouse_pos):
                print("150 CC selected!")
                selected_speed = 'speed3'
                PLAYER_SPEED = SPEED_PLAYER_SPEED[selected_speed]
                recompute_obstacle_speed()
            elif speed4_button.collidepoint(mouse_pos):
                print("200 CC selected!")
                selected_speed = 'speed4'
                PLAYER_SPEED = SPEED_PLAYER_SPEED[selected_speed]
                recompute_obstacle_speed()

            # Players
            elif one_player_button.collidepoint(mouse_pos):
                print("1 Player selected!")
                selected_players = 1
            elif two_player_button.collidepoint(mouse_pos):
                print("2 Players selected!")
                selected_players = 2

    # -- Per-screen update + draw -------------------------------------------
    if current_screen == SCREEN_START:
        draw_start_screen(screen)

    elif current_screen == SCREEN_GAME:
        # ---- Update players ----
        keys = pygame.key.get_pressed()
        if lives[0] > 0:
            player1.update(keys)
        if selected_players == 2 and lives[1] > 0:
            player2.update(keys)

        # ---- Advance the drifting safe corridor ----
        # Move toward the current target; once we're close enough, snap to it
        # and pick a new random target on the road.
        if abs(corridor_center_x - corridor_target_x) < CORRIDOR_DRIFT_SPEED:
            corridor_center_x = corridor_target_x
            corridor_target_x = random.uniform(
                ROAD_LEFT  + CORRIDOR_WIDTH / 2,
                ROAD_RIGHT - CORRIDOR_WIDTH / 2,
            )
        else:
            corridor_center_x += (
                CORRIDOR_DRIFT_SPEED if corridor_target_x > corridor_center_x
                else -CORRIDOR_DRIFT_SPEED
            )

        # ---- Spawn obstacles + coins ----
        # Potholes and rocks avoid the corridor; coins can spawn anywhere
        # (including inside the corridor) so grabbing them is a real risk.
        spawn_timer += 1
        if spawn_timer >= SPAWN_EVERY:
            spawn_timer = 0
            x = random_x_avoiding_corridor(pothole_image.get_width())
            obstacles_list.add(Pothole(x, 0))

        spawn_timer_coins += 1
        if spawn_timer_coins >= SPAWN_EVERY_COINS:
            spawn_timer_coins = 0
            x = random.randint(ROAD_LEFT, ROAD_RIGHT - coin_gif[0].get_width())
            coins_list.add(Coin(x, 0))

        spawn_timer_rocks += 1
        if spawn_timer_rocks >= SPAWN_EVERY_ROCKS:
            spawn_timer_rocks = 0
            x = random_x_avoiding_corridor(rock_image.get_width())
            obstacles_list.add(Rock(x, 0))

        obstacles_list.update()
        coins_list.update()

        # ---- Draw: scrolling background, then obstacles + coins ----
        # Two tiles stacked vertically so the seam is always off-screen.
        bg_rect = RACING_BACKGROUND.get_rect()
        bg_rect.y = (pygame.time.get_ticks() // 10) % GAME_HEIGHT - GAME_HEIGHT
        screen.blit(RACING_BACKGROUND, bg_rect)
        screen.blit(RACING_BACKGROUND, bg_rect.move(0, GAME_HEIGHT))
        obstacles_list.draw(screen)
        coins_list.draw(screen)

        # ---- Collisions & pickups ----
        if lives[0] > 0:
            handle_player_collision(0, player1)
        if selected_players == 2 and lives[1] > 0:
            handle_player_collision(1, player2)
        if lives[0] > 0:
            handle_coin_collection(0, player1)
        if selected_players == 2 and lives[1] > 0:
            handle_coin_collection(1, player2)
        handle_player_push()

        # If handle_player_collision triggered a game over, resize the window
        # back to the start size right away so the next frame renders correctly.
        if current_screen == SCREEN_START:
            screen = pygame.display.set_mode(START_SIZE)
        else:
            # ---- Immunity flash + cars on top ----
            if lives[0] > 0 and immunity[0] > 0:
                immunity[0] -= 1
                if immunity[0] % 10 < 5:                 # flash every 5 frames
                    flash_rect = CAR_FLASHING.get_rect(center=player1.rect.center)
                    screen.blit(CAR_FLASHING, flash_rect)
            if selected_players == 2 and lives[1] > 0 and immunity[1] > 0:
                immunity[1] -= 1
                if immunity[1] % 10 < 5:
                    flash_rect = CAR_FLASHING.get_rect(center=player2.rect.center)
                    screen.blit(CAR_FLASHING, flash_rect)

            if lives[0] > 0:
                screen.blit(player1.image, player1.rect)
            if selected_players == 2 and lives[1] > 0:
                screen.blit(player2.image, player2.rect)

            # ---- Score tick ----
            if lives[0] > 0:
                score[0] += 1
            if selected_players == 2 and lives[1] > 0:
                score[1] += 1

            # ---- HUD ----
            lives_text1 = font_small.render(f"Lives: {lives[0]}", True, (255, 0, 0))
            score_text1 = font_small.render(f"Score: {score[0]}", True, (255, 255, 255))
            screen.blit(lives_text1, (10, 10))
            screen.blit(score_text1, (10, 40))

            if selected_players == 2:
                lives_text2 = font_small.render(f"Lives: {lives[1]}", True, (0, 0, 255))
                score_text2 = font_small.render(f"Score: {score[1]}", True, (255, 255, 255))
                screen.blit(lives_text2, (490, 10))
                screen.blit(score_text2, (490, 40))

    elif current_screen == SCREEN_SETTINGS:
        draw_settings_screen(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()
