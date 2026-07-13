import pygame
import sys

# ============================================================================
# PYGAME SIMPLE TUTORIAL - Learn the basics with detailed explanations
# ============================================================================

# Initialize Pygame
pygame.init()

# ============================================================================
# 1. SCREEN SETUP - Define your game window
# ============================================================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#                                  ^width      ^height
# This creates a window 800 pixels wide and 600 pixels tall

pygame.display.set_caption("Pygame Tutorial - Screens & Shapes")
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

# ============================================================================
# 3. FONTS - For displaying text
# ============================================================================
font_large = pygame.font.Font(None, 72)   # None = default font, 72 = size
font_small = pygame.font.Font(None, 36)


# ============================================================================
# 4. SCREEN STATES - We'll use this variable to switch between screens
# ============================================================================
# 0 = Start Screen, 1 = Game Screen
current_screen = 0


# ============================================================================
# 5. FUNCTION: DRAW START SCREEN
# ============================================================================
def draw_start_screen():
    """This function draws the start screen"""
    screen.fill(BLACK)  # Fill entire screen with black
    #          ^color (RGB tuple)

    # Draw a title
    title = font_large.render("PYGAME DEMO", True, WHITE)
    #                         ^text    ^smooth ^color
    screen.blit(title, (150, 100))
    #           ^what to draw, ^where to draw it (x, y position)

    # Draw instructions
    instructions = font_small.render("Press SPACE to Start Game", True, YELLOW)
    screen.blit(instructions, (150, 250))

    instructions2 = font_small.render("Press ESC to Quit", True, YELLOW)
    screen.blit(instructions2, (150, 320))


# ============================================================================
# 6. FUNCTION: DRAW GAME SCREEN
# ============================================================================
def draw_game_screen():
    """This function draws the game/main screen"""
    screen.fill(BLUE)  # Fill screen with blue background

    # ========================================================================
    # DRAWING SHAPES - Each line shows a different shape with explanations
    # ========================================================================

    # RECTANGLE
    pygame.draw.rect(screen, RED, (50, 50, 150, 100))
    #                ^what   ^color ^x,  y,  width, height
    # This draws a RED rectangle at position (50,50) that is 150 wide and 100 tall
    # Coordinates: x=50 pixels from left, y=50 pixels from top


    # CIRCLE
    pygame.draw.circle(screen, GREEN, (400, 150), 50)
    #                  ^what   ^color ^center x,y  ^radius
    # This draws a GREEN circle centered at (400, 150) with radius of 50 pixels


    # LINE
    pygame.draw.line(screen, YELLOW, (50, 300), (400, 300), 5)
    #                ^what  ^color  ^start point ^end point   ^thickness
    # This draws a YELLOW line from (50,300) to (400,300) with 5 pixel thickness


    # POLYGON (triangle in this case)
    pygame.draw.polygon(screen, WHITE, [(100, 400), (200, 500), (50, 500)])
    #                   ^what   ^color ^list of points (vertices)
    # This draws a WHITE triangle using 3 points
    # Point 1: (100, 400)
    # Point 2: (200, 500)
    # Point 3: (50, 500)


    # ELLIPSE (like a stretched circle)
    pygame.draw.ellipse(screen, (255, 165, 0), (500, 350, 200, 100))
    #                   ^what   ^color orange ^x, y, width, height
    # This draws an ellipse (stretched circle) that is 200 wide and 100 tall


    # ========================================================================
    # DRAW UI TEXT
    # ========================================================================
    title = font_large.render("GAME SCREEN", True, WHITE)
    screen.blit(title, (200, 20))

    instructions = font_small.render("Press P to go back to Start", True, WHITE)
    screen.blit(instructions, (200, 550))


# ============================================================================
# 7. MAIN GAME LOOP
# ============================================================================
running = True

while running:
    clock.tick(FPS)  # Limit to 60 FPS

    # ========================================================================
    # EVENT HANDLING - Check for keyboard and mouse events
    # ========================================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # User clicked X button
            running = False

        elif event.type == pygame.KEYDOWN:  # User pressed a key
            if event.key == pygame.K_ESCAPE:  # ESC key
                running = False

            elif event.key == pygame.K_SPACE:  # SPACE key
                if current_screen == 0:  # If on start screen
                    current_screen = 1  # Go to game screen

            elif event.key == pygame.K_p:  # P key
                if current_screen == 1:  # If on game screen
                    current_screen = 0  # Go back to start screen


    # ========================================================================
    # DRAW THE APPROPRIATE SCREEN
    # ========================================================================
    if current_screen == 0:
        draw_start_screen()
    elif current_screen == 1:
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
# QUICK REFERENCE - COORDINATE SYSTEM
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
#   - At least 3 points needed
#
# pygame.draw.ellipse(surface, color, (x, y, width, height))
#   - Draws an oval/ellipse
#   - Similar to rectangle parameters
#
# ============================================================================
# HOW TO SWITCH SCREENS
# ============================================================================
#
# 1. Create a variable to track current screen:
#    current_screen = 0
#
# 2. Create separate functions for each screen:
#    def draw_start_screen(): ...
#    def draw_game_screen(): ...
#
# 3. Check for key presses in event loop:
#    if event.key == pygame.K_SPACE and current_screen == 0:
#        current_screen = 1
#
# 4. In main loop, draw the right screen:
#    if current_screen == 0:
#        draw_start_screen()
#    elif current_screen == 1:
#        draw_game_screen()
#
# ============================================================================
