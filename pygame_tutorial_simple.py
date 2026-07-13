import pygame
import sys
import math

# ============================================================================
# PYGAME COMPLETE TUTORIAL - Learn basics to advanced features
# Covers: Shapes, Sprites, Collision, Mouse Input, Movement, Animation
# ============================================================================

# Initialize Pygame
pygame.init()

# ============================================================================
# 1. SCREEN SETUP - Define your game window
# ============================================================================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#                                  ^width      ^height
# This creates a window 1000 pixels wide and 700 pixels tall

pygame.display.set_caption("Pygame Tutorial - Complete Guide")
# Sets the title of the window

# ============================================================================
# 2. CLOCK AND COLORS - Control speed and define colors
# ============================================================================
clock = pygame.time.Clock()
FPS = 60  # Frames Per Second - how many times the game updates per second

# Colors are defined as RGB (Red, Green, Blue) tuples
# Each value goes from 0-255
WHITE = (255, 255, 255)   # 255 red, 255 green, 255 blue = white
BLACK = (0, 0, 0)         # 0 of everything = black
RED = (255, 0, 0)         # Full red, no green, no blue
BLUE = (0, 0, 255)        # No red, no green, full blue
GREEN = (0, 255, 0)       # No red, full green, no blue
YELLOW = (255, 255, 0)    # Red + Green = Yellow
CYAN = (0, 255, 255)      # Blue + Green = Cyan
ORANGE = (255, 165, 0)    # Orange color

# ============================================================================
# 3. FONTS - For displaying text
# ============================================================================
font_large = pygame.font.Font(None, 72)   # None = default font, 72 = size
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 28)


# ============================================================================
# 4. SCREEN STATES - We'll use this variable to switch between screens
# ============================================================================
# 0 = Start Screen, 1 = Basic Shapes Demo, 2 = Interactive Game
current_screen = 0


# ============================================================================
# 5. SPRITE CLASS - Creating reusable game objects
# ============================================================================
class Player(pygame.sprite.Sprite):
    """
    A Sprite is a reusable game object.
    Sprites have:
    - image: what they look like (pygame.Surface)
    - rect: their position and size (used for collision detection)
    """

    def __init__(self, x, y):
        super().__init__()  # Initialize the sprite parent class

        # Create the image (a surface) - a 40x40 pixel square
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)  # Color it blue
        #         ^surface, ^color (RGB tuple)

        # Create the rect - tracks position and size
        self.rect = self.image.get_rect()  # Get rectangle from the image
        self.rect.x = x  # X position (pixels from left edge)
        self.rect.y = y  # Y position (pixels from top edge)

        # Movement variables
        self.speed = 5  # How many pixels to move each frame

    def update(self):
        """
        Update is called every frame.
        This is where we handle movement and logic.
        """

        # CONTINUOUS INPUT - Check which keys are currently held down
        keys = pygame.key.get_pressed()
        #       ^gets all currently pressed keys (True/False for each)

        # Move LEFT if A or LEFT arrow is pressed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed  # Subtract from X (move left)
            #          ^position

        # Move RIGHT if D or RIGHT arrow is pressed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed  # Add to X (move right)

        # Move UP if W or UP arrow is pressed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed  # Subtract from Y (move up)

        # Move DOWN if S or DOWN arrow is pressed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed  # Add to Y (move down)

        # Keep player on screen (boundary checking)
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x + self.rect.width > SCREEN_WIDTH:
            self.rect.x = SCREEN_WIDTH - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y + self.rect.height > SCREEN_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def draw(self, surface):
        """Draw this sprite on the given surface"""
        surface.blit(self.image, self.rect)
        #          ^what to draw, ^where (uses rect position)


class Collectible(pygame.sprite.Sprite):
    """An object the player can collect"""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ============================================================================
# 6. GAME STATE VARIABLES
# ============================================================================
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
collectibles = []

# Create some starting collectibles
collectibles.append(Collectible(100, 100))
collectibles.append(Collectible(200, 150))
collectibles.append(Collectible(300, 200))

score = 0
mouse_pos = (0, 0)


# ============================================================================
# 7. SCREEN DRAWING FUNCTIONS
# ============================================================================

def draw_start_screen():
    """This function draws the start screen"""
    screen.fill(BLACK)  # Fill entire screen with black
    #          ^color (RGB tuple)

    # Draw main title
    title = font_large.render("PYGAME TUTORIAL", True, WHITE)
    #                         ^text    ^smooth ^color
    screen.blit(title, (150, 50))
    #           ^what to draw, ^where to draw it (x, y position)

    # Draw subtitle
    subtitle = font_medium.render("Complete Guide", True, CYAN)
    screen.blit(subtitle, (250, 140))

    # Draw menu options
    menu_items = [
        "1. Press 1 - Basic Shapes Demo",
        "2. Press 2 - Interactive Game",
        "",
        "Press ESC - Quit"
    ]

    y_pos = 250
    for item in menu_items:
        text = font_small.render(item, True, YELLOW)
        screen.blit(text, (150, y_pos))
        y_pos += 60


def draw_shapes_screen():
    """Screen showing basic shape drawing with explanations"""
    screen.fill(CYAN)  # Fill screen with cyan background

    # ========================================================================
    # DRAWING SHAPES - Each line shows a different shape with explanations
    # ========================================================================

    # RECTANGLE - Basic 4-sided shape
    pygame.draw.rect(screen, RED, (50, 80, 150, 100))
    #                ^surface ^color ^x,  y,  width, height
    # This draws a RED rectangle at position (50,80) that is 150 wide and 100 tall
    # Coordinates: x=50 pixels from left, y=80 pixels from top

    # CIRCLE - Round shape
    pygame.draw.circle(screen, GREEN, (350, 130), 50)
    #                  ^surface ^color ^center x,y  ^radius
    # This draws a GREEN circle centered at (350, 130) with radius of 50 pixels

    # LINE - Connect two points
    pygame.draw.line(screen, YELLOW, (50, 250), (400, 250), 5)
    #                ^surface ^color  ^start point ^end point   ^thickness
    # This draws a YELLOW line from (50,250) to (400,250) with 5 pixel thickness

    # POLYGON - Shape using multiple points (this is a triangle)
    pygame.draw.polygon(screen, WHITE, [(100, 350), (200, 450), (50, 450)])
    #                   ^surface ^color ^list of points (vertices)
    # This draws a WHITE triangle using 3 points:
    # Point 1: (100, 350)
    # Point 2: (200, 450)
    # Point 3: (50, 450)

    # ELLIPSE - Stretched circle (oval)
    pygame.draw.ellipse(screen, ORANGE, (500, 300, 200, 100))
    #                   ^surface ^color ^x, y, width, height
    # This draws an ORANGE ellipse at (500, 300) that is 200 wide and 100 tall

    # ========================================================================
    # DRAW UI TEXT
    # ========================================================================
    title = font_large.render("SHAPES DEMO", True, WHITE)
    screen.blit(title, (250, 20))

    # Draw a label for each shape
    labels = [
        font_small.render("Rectangle", True, BLACK),
        font_small.render("Circle", True, BLACK),
        font_small.render("Ellipse", True, BLACK),
    ]

    screen.blit(labels[0], (60, 190))
    screen.blit(labels[1], (330, 190))
    screen.blit(labels[2], (520, 410))

    instructions = font_small.render("Press 0 - Back to Menu | Press 2 - Play Game", True, WHITE)
    screen.blit(instructions, (150, 650))


def draw_game_screen():
    """Screen showing sprites, collision, and mouse input"""
    screen.fill(CYAN)  # Fill screen with cyan background

    # ========================================================================
    # DRAW THE PLAYER SPRITE
    # ========================================================================
    player.draw(screen)

    # ========================================================================
    # DRAW COLLECTIBLES
    # ========================================================================
    for collectible in collectibles:
        collectible.draw(screen)

    # ========================================================================
    # DRAW MOUSE POSITION INDICATOR - Visual feedback of mouse location
    # ========================================================================
    pygame.draw.circle(screen, RED, mouse_pos, 10, 2)
    #                  ^surface, ^color, ^center, ^radius, ^width (0=filled, >0=outline)
    # This draws a circle outline at the mouse position
    # width=2 means a 2-pixel thick outline

    # ========================================================================
    # DRAW UI TEXT
    # ========================================================================
    title = font_large.render("INTERACTIVE GAME", True, WHITE)
    screen.blit(title, (200, 20))

    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 70))

    collectible_count = font_small.render(f"Collectibles: {len(collectibles)}", True, WHITE)
    screen.blit(collectible_count, (20, 120))

    mouse_text = font_small.render(f"Mouse: ({mouse_pos[0]}, {mouse_pos[1]})", True, WHITE)
    screen.blit(mouse_text, (20, 160))

    # Draw controls
    controls = [
        "WASD or Arrow Keys - Move",
        "Left Click - Create collectible",
        "Press 0 - Back to Menu | Press 1 - Shapes Demo"
    ]

    y = SCREEN_HEIGHT - 120
    for control in controls:
        text = font_small.render(control, True, WHITE)
        screen.blit(text, (20, y))
        y += 40


# ============================================================================
# 8. MAIN GAME LOOP
# ============================================================================
running = True

while running:
    clock.tick(FPS)  # Limit to 60 FPS

    # ========================================================================
    # EVENT HANDLING - Check for keyboard and mouse events
    # ========================================================================
    for event in pygame.event.get():
        # WINDOW CLOSE EVENT
        if event.type == pygame.QUIT:  # User clicked X button
            running = False

        # KEYBOARD EVENTS (single key press)
        elif event.type == pygame.KEYDOWN:  # User pressed a key
            if event.key == pygame.K_ESCAPE:  # ESC key
                running = False

            # Screen navigation
            elif event.key == pygame.K_0:  # 0 key - Go to start screen
                current_screen = 0
            elif event.key == pygame.K_1:  # 1 key - Go to shapes demo
                current_screen = 1
            elif event.key == pygame.K_2:  # 2 key - Go to game
                current_screen = 2

        # ====================================================================
        # MOUSE MOTION - Track mouse position
        # ====================================================================
        elif event.type == pygame.MOUSEMOTION:
            # MOUSEMOTION fires every time the mouse moves
            mouse_pos = event.pos  # event.pos is a tuple (x, y)
            #         ^x=distance from left, y=distance from top

        # ====================================================================
        # MOUSE BUTTON DOWN - Detect mouse clicks
        # ====================================================================
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # MOUSEBUTTONDOWN fires when a mouse button is pressed
            if event.button == 1:  # 1 = left click, 2 = middle, 3 = right
                if current_screen == 2:  # Only in game screen
                    # Create a new collectible at mouse position
                    collectibles.append(Collectible(mouse_pos[0], mouse_pos[1]))
                    #                                ^x position, ^y position

    # ========================================================================
    # UPDATE GAME STATE
    # ========================================================================
    if current_screen == 2:  # Only update game logic when in game screen
        player.update()  # Update player position based on key presses

        # ====================================================================
        # COLLISION DETECTION - Check if objects touch
        # ====================================================================
        for collectible in collectibles[:]:  # [:] makes a copy of the list
            # rect.colliderect() checks if two rectangles overlap
            if player.rect.colliderect(collectible.rect):
            #  ^player's rect, ^collectible's rect
            # Returns True if they overlap, False if they don't
                score += 10  # Add 10 points
                collectibles.remove(collectible)  # Remove the collectible

                # Create new collectibles in corners
                collectibles.append(Collectible(50, 50))
                collectibles.append(Collectible(SCREEN_WIDTH - 70, 50))

    # ========================================================================
    # DRAW SCREENS
    # ========================================================================
    if current_screen == 0:
        draw_start_screen()
    elif current_screen == 1:
        draw_shapes_screen()
    elif current_screen == 2:
        draw_game_screen()

    # ========================================================================
    # UPDATE DISPLAY
    # ========================================================================
    pygame.display.flip()  # Show everything you drew this frame

# ============================================================================
# CLEANUP
# ============================================================================
pygame.quit()
sys.exit()

# ============================================================================
# COMPREHENSIVE REFERENCE GUIDE
# ============================================================================

# ============================================================================
# COORDINATE SYSTEM
# ============================================================================
# 
# The coordinate system in Pygame:
#
#  (0,0) - Top Left Corner
#    +---------> X increases (going right)
#    |
#    |
#    v Y increases (going down)
#
# Example: Position (300, 200) means:
#   - 300 pixels from the LEFT edge
#   - 200 pixels from the TOP edge
#
# Screen areas:
#   - Top-left: (0, 0)
#   - Top-right: (SCREEN_WIDTH, 0)
#   - Bottom-left: (0, SCREEN_HEIGHT)
#   - Bottom-right: (SCREEN_WIDTH, SCREEN_HEIGHT)

# ============================================================================
# PYGAME.DRAW FUNCTIONS REFERENCE
# ============================================================================
# 
# pygame.draw.rect(surface, color, (x, y, width, height))
#   - Draws a rectangle
#   - x, y = top-left corner position
#   - width, height = size of rectangle
#
# pygame.draw.circle(surface, color, (center_x, center_y), radius)
#   - Draws a circle
#   - center_x, center_y = center point
#   - radius = distance from center to edge
#
# pygame.draw.line(surface, color, (x1, y1), (x2, y2), thickness)
#   - Draws a line
#   - (x1, y1) = starting point
#   - (x2, y2) = ending point
#   - thickness = how thick the line is in pixels
#
# pygame.draw.polygon(surface, color, [(x1, y1), (x2, y2), (x3, y3), ...])
#   - Draws a shape using points
#   - Pass a list of points (tuples)
#   - At least 3 points needed to form a shape
#
# pygame.draw.ellipse(surface, color, (x, y, width, height))
#   - Draws an oval/ellipse
#   - Similar to rectangle parameters
#   - x, y = top-left corner
#   - width, height = size

# ============================================================================
# SPRITES AND RECTS
# ============================================================================
# 
# Sprites are objects that have:
#   - image: pygame.Surface (what they look like)
#   - rect: position and size
#
# Creating a sprite:
#   class MySprite(pygame.sprite.Sprite):
#       def __init__(self):
#           super().__init__()
#           self.image = pygame.Surface((width, height))
#           self.rect = self.image.get_rect()
#           self.rect.x = x_position
#           self.rect.y = y_position
#
# Getting rect properties:
#   sprite.rect.x = 100  # X position
#   sprite.rect.y = 200  # Y position
#   sprite.rect.width = 40  # Width in pixels
#   sprite.rect.height = 40  # Height in pixels
#   sprite.rect.centerx = 500  # Center X position
#   sprite.rect.centery = 300  # Center Y position

# ============================================================================
# COLLISION DETECTION
# ============================================================================
#
# Check if two rectangles overlap:
#   if sprite1.rect.colliderect(sprite2.rect):
#       # They are touching!
#       do_something()
#
# Check if point is inside rectangle:
#   if sprite.rect.collidepoint(mouse_x, mouse_y):
#       # Mouse is over the sprite!

# ============================================================================
# CONTINUOUS INPUT (Holding keys down for smooth movement)
# ============================================================================
#
# pygame.key.get_pressed() returns a list of all keys currently held
# Use in the update() method for smooth movement:
#
#   keys = pygame.key.get_pressed()
#   if keys[pygame.K_RIGHT]:
#       self.x += 5
#
# This checks every frame, so movement is smooth!
# Better than event.type == pygame.KEYDOWN which only fires once

# ============================================================================
# MOUSE EVENTS
# ============================================================================
#
# pygame.MOUSEMOTION:
#   - Fires every time mouse moves
#   - event.pos = (x, y) position
#   - Example: track cursor position
#
# pygame.MOUSEBUTTONDOWN:
#   - Fires when mouse button is pressed
#   - event.button: 1=left, 2=middle, 3=right
#   - event.pos = (x, y) position
#   - Example: click to create objects
#
# pygame.MOUSEBUTTONUP:
#   - Fires when mouse button is released
#   - event.button: 1=left, 2=middle, 3=right

# ============================================================================
# KEY CODES
# ============================================================================
#
# Arrow keys:
#   pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
#
# Letter keys:
#   pygame.K_a, pygame.K_b, ... pygame.K_z
#
# Number keys:
#   pygame.K_0, pygame.K_1, ... pygame.K_9
#
# Special keys:
#   pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_RETURN (Enter)
#   pygame.K_LSHIFT, pygame.K_RSHIFT (left/right shift)
#   pygame.K_LCTRL, pygame.K_RCTRL (left/right control)

# ============================================================================
# HOW TO SWITCH SCREENS
# ============================================================================
#
# 1. Create a variable to track current screen:
#    current_screen = 0
#
# 2. Create separate functions for each screen:
#    def draw_screen_1(): ...
#    def draw_screen_2(): ...
#    def draw_screen_3(): ...
#
# 3. Check for key presses in event loop:
#    if event.key == pygame.K_1:
#        current_screen = 1
#
# 4. In main loop, draw the right screen:
#    if current_screen == 0:
#        draw_screen_1()
#    elif current_screen == 1:
#        draw_screen_2()

# ============================================================================
# GAME LOOP STRUCTURE
# ============================================================================
#
# while running:
#     clock.tick(FPS)          # Control frame rate
#
#     # 1. EVENTS
#     for event in pygame.event.get():
#         # Handle input here
#
#     # 2. UPDATE
#     # Update game logic, positions, collisions
#
#     # 3. DRAW
#     screen.fill(BLACK)        # Clear screen
#     # Draw everything
#     pygame.display.flip()     # Update display
#
# pygame.quit()

# ============================================================================
