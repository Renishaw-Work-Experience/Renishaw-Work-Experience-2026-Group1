import pygame
pygame.init()
clock = pygame.time.Clock()
border_size = 80
pygame.key.set_repeat(6, 6)

def keypressed(keys):
#    if keys[pygame.K_w]:
#        print("Up arrow key pressed")
#    if keys[pygame.K_s]:
#        print("Down arrow key pressed")
    if keys[pygame.K_a]:
        print("Left arrow key pressed")
    if keys[pygame.K_d]:
        print("Right arrow key pressed")

screen_car = pygame.display.set_mode((500, 600))
pygame.display.set_caption("Car Movement Simulation")
screen_car.fill((255, 255, 255))

class Player(pygame.sprite.Sprite):

    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.Surface((50, 80))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, keys):
#        if keys[pygame.K_w]:
#            self.rect.y -= 5
#        if keys[pygame.K_s]:
#            self.rect.y += 5
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if self.rect.x > border_size:  # Prevent moving off the left edge
                self.rect.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.rect.x < 500 - border_size - self.rect.width:  # Prevent moving off the right edge
                self.rect.x += 1

    def draw(self, surface):
        """Draw this sprite on the given surface"""
        surface.blit(self.image, self.rect)

class background(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((360, 600))
        self.image.fill((50,50,50))
        self.rect = self.image.get_rect()
        self.rect.x = (500 - 360) // 2  # Center the background horizontally
        self.rect.y = 0
    
    def draw(self, surface):
        """Draw this sprite on the given surface"""
        surface.blit(self.image, self.rect)

player = Player(200,500)
background = background()

# Game loop
running = True
while running:
    clock.tick(24)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT]:
            keys = pygame.key.get_pressed()
            keypressed(keys)
            player.update(keys)
            print("Event Recieved")
    
        if event.type == pygame.QUIT:
            running = False
    screen_car.fill((100, 255, 100))
    background.draw(screen_car)
    player.draw(screen_car)
    pygame.display.flip()


# Quit Pygame
pygame.quit()