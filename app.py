

import pygame
import pygame.display

import sys
import os
import random


# ---------------------------------------------------------------------------
# Pygame init + display
# ---------------------------------------------------------------------------


pygame.init()
pygame.display.set_caption("Racing Game")

screen = pygame.display.set_mode((600, 600))
clock  = pygame.time.Clock()

font_large  = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small  = pygame.font.Font(None, 28)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Framerate
FPS = 60

# Screen-state IDs (values of `current_screen`).
SCREEN_START    = 0
SCREEN_GAME     = 1
SCREEN_SETTINGS = 2

# Game window / road geometry.
GAME_WIDTH  = 600
GAME_HEIGHT = 600
ROAD_WIDTH  = 420
ROAD_LEFT   = (GAME_WIDTH - ROAD_WIDTH) // 2   #  90 — x where the road starts
ROAD_RIGHT  = ROAD_LEFT + ROAD_WIDTH           # 510 — x where the road ends

# Player start positions (used at boot and by reset_game()).
PLAYER1_START = (200, 500)
PLAYER2_START = (350, 500)

# Movement speeds (all in pixels per frame).
PLAYER_SPEED   = 4     # WASD / arrow-key move speed
COIN_SPEED     = 5     # how fast coins fall
OBSTACLE_SPEED = 5     # how fast rocks & potholes fall
PUSH_SPEED     = 5     # how hard players shove each other on contact

# Spawn rates (in frames — at FPS=60, 60 frames ≈ 1 second).
SPAWN_EVERY       = 60    # pothole every ~1s
SPAWN_EVERY_COINS = 90    # coin every ~1.5s
SPAWN_EVERY_ROCKS = 120   # rock every ~2s

# Scoring & lives.
STARTING_LIVES   = 3
IMMUNITY_FRAMES  = 60    # frames of post-collision invincibility
COIN_SCORE_BONUS = 500   # extra score points for picking up a coin


# ---------------------------------------------------------------------------
# Global state (per-player state uses index 0 = player1, index 1 = player2)
# ---------------------------------------------------------------------------

lives    = [STARTING_LIVES,  STARTING_LIVES]
immunity = [IMMUNITY_FRAMES, IMMUNITY_FRAMES]
score    = [0, 0]

spawn_timer       = 0
spawn_timer_coins = 0
spawn_timer_rocks = 0

current_screen = SCREEN_START


# ---------------------------------------------------------------------------
# Asset-loading helpers (with safe fallbacks so the game still runs when a
# PNG isn't on disk).
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
    pygame.draw.rect(surface, colour,          (8, 8, 34, 64))    # body
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

# UI images (new in file1).
PLAYER_1_CAR = trim_image(load_or_fallback("player_1car.png.png",
create_player_surface((220, 40, 40))))
PLAYER_2_CAR = trim_image(load_or_fallback("player2_car.png.png",
create_player_surface((40, 40, 220))))
START_SCREEN_BACKGROUND = load_or_fallback("start_screen_background.png.jpg",
pygame.Surface((600, 600)))
RACING_BACKGROUND       = load_or_fallback("racing_background.png.png",
pygame.Surface((600, 600)))
CAR_FLASHING            = load_or_fallback("car_flashing.png.png",
pygame.Surface((60, 90), pygame.SRCALPHA))


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
        # Tick the per-sprite animation timer and swap frames when it fires.
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
        self.mask  = pygame.mask.from_surface(self.image)   # for pixel-perfect collision

    def update(self):
        self.rect.y += OBSTACLE_SPEED
        if self.rect.top > screen.get_height():
            self.kill()


class Pothole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pothole_image
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.mask  = pygame.mask.from_surface(self.image)   # for pixel-perfect collision

    def update(self):
        self.rect.y += OBSTACLE_SPEED
        if self.rect.top > screen.get_height():
            self.kill()


class Player(pygame.sprite.Sprite):
    """Two-player controller (WASD for P1, arrow keys for P2)."""

    def __init__(self, x, y, player_num, image):
        super().__init__()
        self.player_num = player_num
        self.image = image
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.mask  = pygame.mask.from_surface(self.image)   # for pixel-perfect collision

    def update(self, keys):
        if (keys[pygame.K_a] and self.player_num == 1) or (keys[pygame.K_LEFT]  and self.player_num == 2):
            if self.rect.x > ROAD_LEFT:
                self.rect.x -= PLAYER_SPEED
        if (keys[pygame.K_d] and self.player_num == 1) or (keys[pygame.K_RIGHT] and self.player_num == 2):
            if self.rect.x < ROAD_RIGHT - self.rect.width:
                self.rect.x += PLAYER_SPEED
        if (keys[pygame.K_w] and self.player_num == 1) or (keys[pygame.K_UP]    and self.player_num == 2):
            if self.rect.y > 0:
                self.rect.y -= PLAYER_SPEED
        if (keys[pygame.K_s] and self.player_num == 1) or (keys[pygame.K_DOWN]  and self.player_num == 2):
            if self.rect.y < GAME_HEIGHT - self.rect.height:
                self.rect.y += PLAYER_SPEED


class Background(pygame.sprite.Sprite):
    """Static grey road strip — fallback when RACING_BACKGROUND is missing."""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ROAD_WIDTH, GAME_HEIGHT))
        self.image.fill((50, 50, 50))          # dark grey road
        self.rect  = self.image.get_rect(topleft=(ROAD_LEFT, 0))


# ---------------------------------------------------------------------------
# Sprite instances, groups, and UI rects
# ---------------------------------------------------------------------------

player1 = Player(*PLAYER1_START, 1, PLAYER_1_CAR)   # Red car for player 1
player2 = Player(*PLAYER2_START, 2, PLAYER_2_CAR)   # Blue car for player 2

player_group   = pygame.sprite.Group(player1, player2)
coins_list     = pygame.sprite.Group()
obstacles_list = pygame.sprite.Group()
bg = Background()

# Buttons at MODULE scope so both the drawing function and the event
# handler can see them.  (x, y, width, height)
start_button    = pygame.Rect(255, 200, 100, 50)
settings_button = pygame.Rect(230, 280, 150, 50)


# ---------------------------------------------------------------------------
# Drawing functions
# ---------------------------------------------------------------------------

def draw_start_screen(surface):
    surface.blit(START_SCREEN_BACKGROUND, (0, -350))

    title         = font_small.render("Racing Game", True, (255, 255, 255))
    start_text    = font_small.render("START",       True, (0, 0, 139))
    settings_text = font_small.render("SETTINGS",    True, (255, 0, 0))

    surface.blit(title,         (245, 150))
    surface.blit(start_text,    (275, 215))
    surface.blit(settings_text, (255, 295))

    pygame.draw.rect(surface, (0, 0, 139), start_button,    4)
    pygame.draw.rect(surface, (255, 0, 0), settings_button, 4)


def draw_settings_screen(surface):
    surface.fill((0, 0, 0))

    title       = font_small.render("Settings",      True, (255, 255, 255))
    placeholder = font_small.render("(coming soon)", True, (150, 150, 150))

    surface.blit(title,       (155,  50))
    surface.blit(placeholder, (130, 110))


# ---------------------------------------------------------------------------
# Game-flow helpers
# ---------------------------------------------------------------------------

def reset_game():
    """Reset all game state after a game over."""
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
            if lives[0] <= 0 and lives[1] <= 0:
                print("Game Over!")
                current_screen = SCREEN_START
                reset_game()
            elif lives[player_index] <= 0:
                print(f"Player {player_index + 1} has lost all lives!")
                player_sprite.rect.topleft = (1000, 1000)   # move off-screen
            break


def handle_coin_collection(player_index, player_sprite):
    """Check coins vs one player; pick up (remove) each coin and award score.

    Uses rect collision (not mask) because the coin sprite's image swaps every
    animation frame, which would make a cached mask go out of sync.
    """
    for coin in coins_list:
        if player_sprite.rect.colliderect(coin.rect):
            coin.kill()
            score[player_index] += COIN_SCORE_BONUS
            print(f"Player {player_index + 1} collected a coin! (+{COIN_SCORE_BONUS})")


def handle_player_push():
    """Push the two players apart when they overlap (only if both are alive)."""
    if lives[0] <= 0 or lives[1] <= 0:
        return
    if not player1.rect.colliderect(player2.rect):
        return

    # Vertical push
    if player1.rect.y > player2.rect.y:
        if player1.rect.y < screen.get_height() - player1.rect.height:
            player1.rect.y += PUSH_SPEED     # push player 1 down
        if player2.rect.y > 0:
            player2.rect.y -= PUSH_SPEED     # push player 2 up
    elif player1.rect.y < player2.rect.y:
        if player1.rect.y > 0:
            player1.rect.y -= PUSH_SPEED     # push player 1 up
        if player2.rect.y < screen.get_height() - player2.rect.height:
            player2.rect.y += PUSH_SPEED     # push player 2 down

    # Horizontal push
    if player1.rect.x > player2.rect.x:
        if player1.rect.x < ROAD_RIGHT - player1.rect.width:
            player1.rect.x += PUSH_SPEED     # push player 1 right
        if player2.rect.x > ROAD_LEFT:
            player2.rect.x -= PUSH_SPEED     # push player 2 left
    elif player1.rect.x < player2.rect.x:
        if player1.rect.x > ROAD_LEFT:
            player1.rect.x -= PUSH_SPEED     # push player 1 left
        if player2.rect.x < ROAD_RIGHT - player2.rect.width:
            player2.rect.x += PUSH_SPEED     # push player 2 right


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

running = True
while running:
    clock.tick(FPS)

    # -- Event handling -----------------------------------------------------
    # ONE event loop — pygame.event.get() drains the queue, so calling it twice
    # per frame silently eats the events (which is why the buttons weren't working).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Only react to clicks while on the start screen.
        if current_screen == SCREEN_START and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if start_button.collidepoint(mouse_pos):
                print("Start button clicked!")
                current_screen = SCREEN_GAME
            elif settings_button.collidepoint(mouse_pos):
                print("Settings button clicked!")
                current_screen = SCREEN_SETTINGS

    # -- Draw + update per state --------------------------------------------
    if current_screen == SCREEN_START:
        draw_start_screen(screen)

    elif current_screen == SCREEN_GAME:
        # Update the players from held keys (continuous movement, once per frame).
        keys = pygame.key.get_pressed()
        if lives[0] > 0:
            player1.update(keys)
        if lives[1] > 0:
            player2.update(keys)

        # Spawn a new pothole every SPAWN_EVERY frames.
        spawn_timer += 1
        if spawn_timer >= SPAWN_EVERY:
            spawn_timer = 0
            x = random.randint(ROAD_LEFT, ROAD_RIGHT - pothole_image.get_width())
            obstacles_list.add(Pothole(x, 0))

        # Spawn a new coin every SPAWN_EVERY_COINS frames.
        spawn_timer_coins += 1
        if spawn_timer_coins >= SPAWN_EVERY_COINS:
            spawn_timer_coins = 0
            x = random.randint(ROAD_LEFT, ROAD_RIGHT - coin_gif[0].get_width())
            coins_list.add(Coin(x, 0))

        # Spawn a new rock every SPAWN_EVERY_ROCKS frames.
        spawn_timer_rocks += 1
        if spawn_timer_rocks >= SPAWN_EVERY_ROCKS:
            spawn_timer_rocks = 0
            x = random.randint(ROAD_LEFT, ROAD_RIGHT - rock_image.get_width())
            obstacles_list.add(Rock(x, 0))

        obstacles_list.update()
        coins_list.update()

        # Draw: scrolling racing background, then obstacles + coins.  Two tiles
        # stacked vertically so the seam is always off-screen.
        bg_rect = RACING_BACKGROUND.get_rect()
        bg_rect.y = (pygame.time.get_ticks() // 10) % GAME_HEIGHT - GAME_HEIGHT
        screen.blit(RACING_BACKGROUND, bg_rect)
        screen.blit(RACING_BACKGROUND, bg_rect.move(0, GAME_HEIGHT))
        obstacles_list.draw(screen)                # potholes & rocks
        coins_list.draw(screen)                    # animated coins

        # Collisions & pickups.
        if lives[0] > 0:
            handle_player_collision(0, player1)
        if lives[1] > 0:
            handle_player_collision(1, player2)
        if lives[0] > 0:
            handle_coin_collection(0, player1)
        if lives[1] > 0:
            handle_coin_collection(1, player2)
        handle_player_push()

        # Immunity flash overlay — draw the halo BEHIND the car, then the car.
        if lives[0] > 0 and immunity[0] > 0:
            immunity[0] -= 1
            if immunity[0] % 10 < 5:                # flash every 5 frames
                flash_rect = CAR_FLASHING.get_rect(center=player1.rect.center)
                screen.blit(CAR_FLASHING, flash_rect)
        if lives[1] > 0 and immunity[1] > 0:
            immunity[1] -= 1
            if immunity[1] % 10 < 5:                # flash every 5 frames
                flash_rect = CAR_FLASHING.get_rect(center=player2.rect.center)
                screen.blit(CAR_FLASHING, flash_rect)

        # Cars on top of any flashing halo.
        if lives[0] > 0:
            screen.blit(player1.image, player1.rect)   # red car
        if lives[1] > 0:
            screen.blit(player2.image, player2.rect)   # blue car

        # Score ticks up 1/frame while the player is alive.
        if lives[0] > 0:
            score[0] += 1
        if lives[1] > 0:
            score[1] += 1

        # HUD — left column = player 1, right column = player 2.
        lives_text1 = font_small.render(f"Lives: {lives[0]}", True, (255, 0, 0))
        lives_text2 = font_small.render(f"Lives: {lives[1]}", True, (0, 0, 255))
        score_text1 = font_small.render(f"Score: {score[0]}", True, (255, 255, 255))
        score_text2 = font_small.render(f"Score: {score[1]}", True, (255, 255, 255))
        screen.blit(lives_text1, ( 10, 10))
        screen.blit(lives_text2, (490, 10))
        screen.blit(score_text1, ( 10, 40))
        screen.blit(score_text2, (490, 40))

    elif current_screen == SCREEN_SETTINGS:
        draw_settings_screen(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()
