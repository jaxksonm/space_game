# massive credit to https://www.youtube.com/watch?v=GiUGVOqqCKg
# for helping me understand the basics of pygame and providing the framework for this game
import pygame
from pygame.locals import *
import random  # RNG 😡😡😡

pygame.init()  # initialize pygame
# game icon
icon = pygame.image.load(r"space_sprites/ship001.png")
pygame.display.set_icon(icon)  # set the icon

clock = pygame.time.Clock()
fps = 60  # game speed

# dimension vars
WIDTH = 900
HEIGHT = 600
font = pygame.font.SysFont('Arial', 30)  # font for game
font2 = pygame.font.SysFont('Courier', 60, bold=True)  # font for menu

# screen size
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # window size
pygame.display.set_caption('Space Shooter')


def show_menu():
    menu_running = True
    while menu_running:
        # load game background into menu
        menu_background = pygame.image.load(r"space_sprites/output-onlinepngtools.png")
        menu_background = pygame.transform.scale(menu_background, (WIDTH + 50, HEIGHT))
        screen.blit(menu_background, (0, 0))  # display the menu

        button_bg_color = (200, 200, 200)  # background color gray
        text_color = (255, 255, 255)  # text color white

        # text boxes
        play_text = font2.render("PLAY", True, text_color)
        quit_text = font2.render("QUIT", True, text_color)

        # center the buttons
        play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        # add padding so that buttons are clickable in a box
        play_bg_rect = play_rect.inflate(20, 10)
        quit_bg_rect = quit_rect.inflate(20, 10)

        # draw backgrounds
        pygame.draw.rect(screen, button_bg_color, play_bg_rect, border_radius=5)
        pygame.draw.rect(screen, button_bg_color, quit_bg_rect, border_radius=5)

        # draw text
        screen.blit(play_text, play_rect)
        screen.blit(quit_text, quit_rect)

        # event handling
        for events in pygame.event.get():
            if events.type == QUIT:
                pygame.quit()
                exit()
            if events.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # if the user clicks play, play again
                if play_bg_rect.collidepoint(mouse_pos):
                    menu_running = False

                if quit_bg_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()

        pygame.display.update()


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
game_paused = False
score = 0  # set score to 0
# load images
background = pygame.image.load(r"space_sprites/output-onlinepngtools.png")
background = pygame.transform.scale(background,
                                    (WIDTH + 50, HEIGHT))  # slightly bigger than screen so scrolling will hide

button_image = pygame.image.load(r"space_sprites/text-1734273102144.png")
button_image = pygame.transform.scale(button_image, (200, 150))


def reset_game():
    # empty obstacle groups
    obstacle_group.empty()
    blaster_group.empty()

    # reposition the ship
    ship.rect.x = 50
    ship.rect.y = int(HEIGHT / 2)
    ship.velocity = 0

    # set the score to 0
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
            b_image_width, b_image_height = background_image.get_size()
            x_position = (WIDTH - b_image_width) / 2
            y_position = (HEIGHT - b_image_height) / 2
            screen.blit(background_image, (x_position, y_position))


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
image_width, image_height = button_image.get_size()
x_pos = (WIDTH - image_width) / 2
y_pos = (HEIGHT - image_height) / 2
button = Button(x_pos, y_pos + 200, button_image)

blaster_fired = False  # check if the blaster was shot
run = True
show_menu()
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
        if event.type == KEYDOWN:
            if event.key == K_p:
                game_paused = True
                show_menu()

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
