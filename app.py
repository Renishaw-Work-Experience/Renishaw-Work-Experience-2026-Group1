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
lives = [3, 3]        # lives[0] for player1, lives[1] for player2
immunity = [60, 60]   # frames of immunity after a collision for player1 and player2
score = [0, 0]        # score[0] for player1, score[1] for player2


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


# Speeds / spawn rates
SPAWN_EVERY       = 60      # spawn one pothole every 60 frames (~1 second)
SPAWN_EVERY_COINS = 90      # spawn one coin every 90 frames (~1.5 seconds)
SPAWN_EVERY_ROCKS = 120     # spawn one rock every 120 frames (~2 seconds)
COIN_SPEED        = 5       # px/frame — how fast coins fall
OBSTACLE_SPEED    = 5       # px/frame — how fast rocks & potholes fall


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
        self.image = pothole_image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.y += OBSTACLE_SPEED             # Move the pothole down
        if self.rect.top > screen.get_height():   # Throw it away once it leaves the screen
            self.kill()


coins_list       = pygame.sprite.Group()
obstacles_list   = pygame.sprite.Group()
spawn_timer      = 0
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
        self.player_num = player_num
        self.image = pygame.Surface((50, 80))
        self.image.fill(colour)
        self.rect = self.image.get_rect(topleft=(x, y))

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

        # Draw: green surround, then the road, then obstacles + coins, then the players on top.
        screen.fill((100, 255, 100))                       # grass
        screen.blit(bg.image, bg.rect)                     # road
        obstacles_list.draw(screen)                        # potholes & rocks
        coins_list.draw(screen)                            # animated coins
        screen.blit(player1.image, player1.rect)           # red car
        screen.blit(player2.image, player2.rect)           # blue car

        if (player1.rect.colliderect(obstacles_list.sprites()[0].rect) if obstacles_list else False) and immunity[0] == 0:
            print("Collision detected!")
            lives[0] -= 1
            immunity[0] = 60  # frames of immunity for player1 after a collision
            obstacles_list.sprites()[0].kill()  # Remove the obstacle that was hit
            if lives[0] <= 0 and lives[1] <= 0:
                print("Game Over!")
                current_screen = 0
                for obsticles in obstacles_list:
                    obstacles_list.remove(obsticles)
                for coin in coins_list:
                    coins_list.remove(coin)
                screen = pygame.display.set_mode((400, 300))   # resize back to start screen
                lives = [3, 3]
                score = [0, 0]
                player1.rect.topleft = (200, 500)  # Reset player1 position
                player2.rect.topleft = (300, 500)  # Reset player2 position
            elif lives[0] <= 0:
                print("Player 1 has lost all lives!")
                player1.rect.topleft = (1000, 1000) # Move player1 off-screen

        if (player2.rect.colliderect(obstacles_list.sprites()[0].rect) if obstacles_list else False) and immunity[1] == 0:
            print("Collision detected!")
            lives[1] -= 1
            immunity[1] = 60  # frames of immunity for player2 after a collision
            obstacles_list.sprites()[0].kill()  # Remove the obstacle that was hit
            if lives[0] <= 0 and lives[1] <= 0:
                print("Game Over!")
                current_screen = 0
                for obsticles in obstacles_list:
                    obstacles_list.remove(obsticles)
                for coin in coins_list:
                    coins_list.remove(coin)
                screen = pygame.display.set_mode((400, 300))   # resize back to start screen
                lives = [3, 3]
                score = [0, 0]
                player1.rect.topleft = (200, 500)  # Reset player1 position
                player2.rect.topleft = (300, 500)  # Reset player2 position
            elif lives[1] <= 0:
                print("Player 2 has lost all lives!")
                player2.rect.topleft = (1000, 1000) # Move player2 off-screen

        if (player1.rect.colliderect(coins_list.sprites()[0].rect) if coins_list else False):
            print("Coin collected by Player 1!")
            score[0] += 250  # Increment score for player1
            coins_list.sprites()[0].kill()  # Remove the coin that was collected
        
        if (player2.rect.colliderect(coins_list.sprites()[0].rect) if coins_list else False):
            print("Coin collected by Player 2!")
            score[1] += 250  # Increment score for player2
            coins_list.sprites()[0].kill()  # Remove the coin that was collected

        if (player1.rect.colliderect(player2.rect)):
            pygame.display.flip()
            if player1.rect.y > player2.rect.y:
                if player1.rect.y < screen.get_height() - player1.rect.height:
                    player1.rect.y += 5  # push player 1 down
                if player2.rect.y > 0:
                    player2.rect.y -= 5  # push player 2 up
            elif player1.rect.y < player2.rect.y:
                if player1.rect.y > 0:
                    player1.rect.y -= 5  # push player 1 up
                if player2.rect.y < screen.get_height() - player2.rect.height:
                    player2.rect.y += 5  # push player 2 down
            if player1.rect.x > player2.rect.x:
                if player1.rect.x < ROAD_RIGHT - player1.rect.width:
                    player1.rect.x += 5  # push player 1 right
                if player2.rect.x > ROAD_LEFT:
                    player2.rect.x -= 5  # push player 2 left
            elif player1.rect.x < player2.rect.x:
                if player1.rect.x > ROAD_LEFT:
                    player1.rect.x -= 5  # push player 1 left
                if player2.rect.x < ROAD_RIGHT - player2.rect.width:
                    player2.rect.x += 5  # push player 2 right

        if immunity[0] > 0:
            immunity[0] -= 1
            # Draw a visual indicator for immunity1 (e.g., a flashing effect)
            if immunity[0] % 10 < 5:  # Flash every 5 frames
                pygame.draw.rect(screen, (255, 255, 0), player1.rect, 3)  # Yellow border around the player1
        
        if immunity[1] > 0:
            immunity[1] -= 1
            # Draw a visual indicator for immunity2 (e.g., a flashing effect)
            if immunity[1] % 10 < 5:  # Flash every 5 frames
                pygame.draw.rect(screen, (255, 255, 0), player2.rect, 3)  # Yellow border around the player2

        if lives[0] > 0:
            score[0] += 1  # Increment score1 every frame
        if lives[1] > 0:
            score[1] += 1  # Increment score2 every frame

        lives_text1 = font_small.render(f"Lives: {lives[0]}", True, (255, 0, 0))
        screen.blit(lives_text1, (10, 10))
        lives_text2 = font_small.render(f"Lives: {lives[1]}", True, (0, 0, 255))
        screen.blit(lives_text2, (380, 10))

        score_text1 = font_small.render(f"Score: {score[0]}", True, (255, 255, 255))
        screen.blit(score_text1, (10, 40))
        score_text2 = font_small.render(f"Score: {score[1]}", True, (255, 255, 255))
        screen.blit(score_text2, (380, 40))

    elif current_screen == 2:
        draw_settings_screen(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()

