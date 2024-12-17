# massive credit to https://www.youtube.com/watch?v=GiUGVOqqCKg
# for helping me understand the basics of pygame and providing the framework for this game
import pygame
from pygame.locals import *
import random  # RNG 😡😡😡

pygame.init()

clock = pygame.time.Clock()
fps = 60  # game speed

# dimension vars
WIDTH = 900
HEIGHT = 600

# screen size
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # window size
pygame.display.set_caption('Space Shooter')

try:  # try to open the file and read the highscore
    with open("highscore.txt", "r") as file:
        highscore = int(file.read().strip())
except ValueError:
    print("file empty - first game")  # the user's first game will result in an empty file
    highscore = 0  # set their score to 0
# game vars
scroll = 0
scroll_speed = 10  # scroll speed can be adjusted to alter difficulty
flying = False
game_over = False
obstacle_frequency = 400  # change the frequency to alter game difficulty
last_obstacle = pygame.time.get_ticks() - obstacle_frequency
blaster_delay = 800  # set the blaster delay in ms
last_blaster = pygame.time.get_ticks() - blaster_delay
MAX_POS = 500
MIN_POS = 100
font = pygame.font.SysFont('Arial', 30)
score = 0
# load images
background = pygame.image.load(r"space_sprites/output-onlinepngtools.png")
background = pygame.transform.scale(background,
                                    (WIDTH + 50, HEIGHT))  # slightly bigger than screen so scrolling will hide

button_image = pygame.image.load(r"space_sprites/text-1734273102144.png")
button_image = pygame.transform.scale(button_image, (200, 150))


def reset_game():
    obstacle_group.empty()
    blaster_group.empty()
    ship.rect.x = 50
    ship.rect.y = int(HEIGHT / 2)
    reset_score = 0
    return reset_score


# rocket class
class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        self.image1 = pygame.image.load(r"space_sprites/ship001.png")
        self.image2 = pygame.image.load(r"space_sprites/ship001.png")
        self.images.append(self.image1)
        self.images.append(self.image2)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.pressed = False

    def update(self):
        if flying:
            self.velocity += 0.5  # invert this for negative gravity
            if self.velocity > 8:
                self.velocity = 8

            if self.rect.bottom < HEIGHT:
                self.rect.y += int(self.velocity)
        if not game_over:
            if pygame.key.get_pressed()[K_SPACE] == 1 and self.pressed == False:
                self.pressed = True
                self.velocity = -10  # make this positive for inverted gravity
            if pygame.key.get_pressed()[K_SPACE] == 0:
                self.pressed = False

            self.counter += 1
            rocket_cooldown = 15

            if self.counter > rocket_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], -self.velocity)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], 180)
            obstacle_group.empty()  # delete all obstacles
            background_image = pygame.image.load(
                r"space_sprites/text-1734188492127.png")
            background_image = pygame.transform.scale(background_image, (700, 200))
            screen.blit(background_image, (WIDTH / 8, HEIGHT - 400))


# obstacle class
class Obstacles(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.MAX = 200
        self.MIN = 100
        self.random_number = random.randint(self.MIN, self.MAX)
        self.get_random_number = self.random_number
        # load obstacles
        self.image1 = pygame.image.load(r"space_sprites/astreroid.png")
        self.image1 = pygame.transform.scale(self.image1, (50, 50))

        self.image2 = pygame.image.load(r"space_sprites/asteroid2.png")
        self.image2 = pygame.transform.scale(self.image2, (50, 50))

        self.image3 = pygame.image.load(r"space_sprites/asteroid2.png")
        self.image3 = pygame.transform.scale(self.image3, (self.get_random_number, self.get_random_number))

        # randomly get select generate an asteroid
        self.image = random.choice([self.image1, self.image2, self.image3])

        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

        if self.image == self.image1 or self.image == self.image2:
            self.hitbox = pygame.Rect(self.rect.centerx - 15, self.rect.centery - 15, 40, 40)
        else:
            self.hitbox = pygame.Rect(self.rect.centerx - 15, self.rect.centery - 15, self.get_random_number - 40,
                                      self.get_random_number - 40)
        # for hit box debugging
        # for obstacle in obstacle_group:
        #   pygame.draw.rect(screen, (255, 0, 0), obstacle.hitbox, 2)

    def update(self):
        self.rect.x -= scroll_speed

        self.hitbox.x = self.rect.x + (self.rect.width // 2) - (self.hitbox.width // 2)
        self.hitbox.y = self.rect.y + (self.rect.height // 2) - (self.hitbox.height // 2)

        # remove the obstacle when it goes off-screen so that it does not kill the computer
        if self.rect.right < 0:
            self.kill()


# blaster class
class Blaster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            r"space_sprites/16.png")
        self.image = pygame.transform.scale(self.image, (120, 50))
        self.rect = self.image.get_rect()
        self.hitbox = pygame.Rect(self.rect.centerx - 15, self.rect.centery - 15, 30, 30)
        self.rect.topleft = [x, y]
        self.velocity_x = 10  # speed of the blaster along the x-axis

    def update(self):
        self.rect.x += self.velocity_x
        self.hitbox.x = self.rect.x + (self.rect.width // 2) - (self.hitbox.width // 2)
        self.hitbox.y = self.rect.y + (self.rect.height // 2) - (self.hitbox.height // 2)

        if self.rect.left > WIDTH + 100:
            self.kill()


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


# game
blaster_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
rocket_group = pygame.sprite.Group()

ship = Rocket(100, int(HEIGHT / 2))
rocket_group.add(ship)

# create restart button
button = Button(WIDTH // 2 - 50, HEIGHT - 140, button_image)

blaster_fired = False  # check if the blaster was shot
run = True

while run:
    clock.tick(fps)

    screen.blit(background, (scroll, 0))

    rocket_group.draw(screen)
    rocket_group.update()
    obstacle_group.draw(screen)

    if pygame.key.get_pressed()[pygame.K_w] and not blaster_fired:
        current_time2 = pygame.time.get_ticks()
        if current_time2 - last_blaster > blaster_delay:
            # position blaster to come out of rocket
            laser = Blaster(ship.rect.centerx + 50, ship.rect.centery)  # Shoot from the rocket
            blaster_group.add(laser)
            last_blaster = current_time2
            blaster_fired = True  # set flag to true so that the user cannot fire multiple blasters

    if not pygame.key.get_pressed()[pygame.K_w]:
        blaster_fired = False  # if w is released reset the flag

    blaster_group.update()
    blaster_group.draw(screen)

    # rocket collision with obstacles
    rocket_collision = pygame.sprite.spritecollideany(ship, obstacle_group)

    if rocket_collision:
        # Check if the rocket actually collides with the obstacle's hitbox
        if ship.rect.colliderect(rocket_collision.hitbox):
            game_over = True

    # blaster collision with obstacles
    for blaster in blaster_group:
        blaster_collision = pygame.sprite.spritecollideany(blaster, obstacle_group)
        if blaster_collision:
            # check if the blaster actually collides with the obstacle's hitbox
            if blaster.hitbox.colliderect(blaster_collision.hitbox):
                blaster.kill()  # destroy the blaster
                blaster_collision.kill()  # destroy the obstacle
                score += 100  # increase player score by 100

    if ship.rect.top + 50 < 0:
        game_over = True

    if ship.rect.bottom >= HEIGHT:
        game_over = True
        flying = False

    if not game_over and flying:
        score += 1
        current_time = pygame.time.get_ticks()
        if current_time - last_obstacle > obstacle_frequency:
            obstacle_position = random.randint(MIN_POS, MAX_POS)
            bottom_obstacle = Obstacles(WIDTH, obstacle_position)
            obstacle_group.add(bottom_obstacle)
            last_obstacle = current_time

        scroll -= scroll_speed
        if abs(scroll) > 40:
            scroll = 0
        obstacle_group.update()

    # check for game over and reset
    if game_over:
        if button.draw():
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

        if event.type == KEYDOWN and flying == False and game_over == False:
            flying = True

    if highscore <= score:
        highscore = score

    text = font.render(f"Score: {score}", True, (255, 255, 255))
    text2 = font.render(f"High Score: {highscore}", True, (255, 255, 255))
    screen.blit(text, (HEIGHT * 2 - WIDTH / 2, 0))
    screen.blit(text2, (HEIGHT * 2 - WIDTH / 2 - 750, 0))
    pygame.display.update()

    if highscore <= score:
        with open("highscore.txt", "w") as file:
            file.write(str(score))

pygame.quit()

# new obstacle that destroys itself when the ship hits it
# lives for the ship
# add sound!
# add a game menu
