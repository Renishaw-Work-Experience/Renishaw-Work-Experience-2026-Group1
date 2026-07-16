#-------------------------------- 2D Retro Car Game ---------------------------------#

#-------- 1. Importing Modules --------#

from cmath import rect
import pygame
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
LIVES = 3
IMMUNITY = 60  # frames of immunity after a collision
SCORE = 0
CURRENT_SCREEN = 0
FONT_LARGE = pygame.font.Font(None, 72)
FONT_MEDIUM = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 28)
OBSTACLES_LIST = pygame.sprite.Group()
SPAWN_TIMER = 0
SPAWN_EVERY = 60                                  # spawn one pothole every 60 frames (~1 second)
GAME_WIDTH   = 600
GAME_HEIGHT  = 600
ROAD_WIDTH   = 420
ROAD_LEFT    = (GAME_WIDTH - ROAD_WIDTH) // 2   # x where the road starts (70)
ROAD_RIGHT   = ROAD_LEFT + ROAD_WIDTH           # x where the road ends   (430)
PLAYER_SPEED = 4                                # pixels per frame
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
RUNNING = True
IMMUNITY = 60  # frames of immunity after a collision

#-------- 5. Classes --------#

if POTHOLE_IMAGE is None:
    POTHOLE_IMAGE = pygame.Surface((60, 30), pygame.SRCALPHA)         # Try to load the pothole PNG; fall back to a drawn shape if the file is missing.
    pygame.draw.ellipse(POTHOLE_IMAGE, (60, 60, 60), POTHOLE_IMAGE.get_rect())
    pygame.draw.ellipse(POTHOLE_IMAGE, (30, 30, 30), POTHOLE_IMAGE.get_rect(), 3)

class Pothole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = POTHOLE_IMAGE
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += 5                          # Move the pothole down by 5 pixels
        if self.rect.top > SCREEN.get_height():   # Throw it away once it leaves the screen
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PLAYER_1_CAR                               # Player 1 Car
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if self.rect.x > ROAD_LEFT:
                self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.rect.x < ROAD_RIGHT - self.rect.width:
                self.rect.x += PLAYER_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if self.rect.y > 0:
                self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if self.rect.y < GAME_HEIGHT - self.rect.height:
                self.rect.y += PLAYER_SPEED

player = Player(200, 500)

#-------- 6. Main Game Loop --------#

while RUNNING:
    CLOCK.tick(FPS)

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
        player.update(keys)

        # Spawn a new pothole every SPAWN_EVERY frames.
        SPAWN_TIMER += 1
        if SPAWN_TIMER >= SPAWN_EVERY:
            SPAWN_TIMER = 0
            x = random.randint(ROAD_LEFT, ROAD_RIGHT - POTHOLE_IMAGE.get_width())
            OBSTACLES_LIST.add(Pothole(x, 0))

        OBSTACLES_LIST.update()

        # Draw: the road, then obstacles, then the player on top.
        # Makes the road background move downwards to give the illusion of movement.
        rect = RACING_BACKGROUND.get_rect()
        rect.y = (pygame.time.get_ticks() // 10) % GAME_HEIGHT - GAME_HEIGHT
        SCREEN.blit(RACING_BACKGROUND, rect)
        OBSTACLES_LIST.draw(SCREEN)                        # potholes
        SCREEN.blit(player.image, player.rect)             # car

        if IMMUNITY == 0 and OBSTACLES_LIST:
            collision = False
            for obstacle in OBSTACLES_LIST:
                if pygame.sprite.collide_mask(player, obstacle):
                    collision = True
                    break

            if collision:
                print("Collision detected!")
                LIVES -= 1
                IMMUNITY = 60  # Give the player a short invincibility window after each hit
                if LIVES <= 0:
                    print("Game Over!")
                    CURRENT_SCREEN = 0
                    for obstacle in list(OBSTACLES_LIST):
                        obstacle.kill()
                    SCREEN = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))   # resize back to start screen
                    LIVES = 3
                    SCORE = 0
                    player.rect.topleft = (200, 500)  # Reset player position
        
        if IMMUNITY > 0:
            IMMUNITY -= 1
            # Draw a visual indicator for immunity (e.g., a flashing effect)
            if IMMUNITY % 10 < 5:  # Flash every 5 frames
                # Draw the yellow outline behind the car so the car appears on top
                flash_rect = CAR_FLASHING.get_rect(center=player.rect.center)
                SCREEN.blit(CAR_FLASHING, flash_rect)
            SCREEN.blit(player.image, player.rect)  # Draw the car on top of the flashing effect
        SCORE += 1  # Increment score every frame
            
        lives_text = FONT_SMALL.render(f"Lives: {LIVES}", True, (255, 0, 0))
        SCREEN.blit(lives_text, (10, 10))
        
        
        score_text = FONT_SMALL.render(f"Score: {SCORE}", True, (255, 255, 255))
        SCREEN.blit(score_text, (10, 40))

    elif CURRENT_SCREEN == 2:
        draw_settings_screen(SCREEN)

    pygame.display.flip()

pygame.quit()
sys.exit()