from settings import *
from random import randrange, choice
import pygame
import os
import sys
import random

pygame.init()

pygame.display.set_icon(pygame.image.load(os.path.join('data', 'dino.png')))
pygame.display.set_caption('Dino Run')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def load_image(image_name, color_key=None):
    fullname = os.path.join('data', image_name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is None:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def draw_text(words, surface, pos, size, colour, font_name, centered=False):
    font = pygame.font.SysFont(font_name, size)
    text = font.render(words, False, colour)
    text_size = text.get_size()
    if centered:
        pos[0] = pos[0] - text_size[0] // 2
        pos[1] = pos[1] - text_size[1] // 2
    surface.blit(text, pos)


def terminate():
    pygame.quit()
    sys.exit()


class Ground:
    """Ground for background"""

    def __init__(self):
        self.image1 = pygame.transform.scale(load_image('ground.png'), (WIDTH, 20))
        self.rect1 = self.image1.get_rect()
        self.rect1.left = 0

        self.image2 = pygame.transform.scale(load_image('ground.png'), (WIDTH, 20))
        self.rect2 = self.image2.get_rect()
        self.rect2.left = WIDTH

        self.rect1.bottom = self.rect2.bottom = HEIGHT - 100

    def update(self):
        if not pause:
            self.rect1.left -= BG_SPEED
            self.rect2.left -= BG_SPEED

            if self.rect1.left < -WIDTH:
                self.rect1.left = self.rect2.right

            if self.rect2.left < -WIDTH:
                self.rect2.left = self.rect1.right

    def draw(self):
        screen.blit(self.image1, self.rect1)
        screen.blit(self.image2, self.rect2)


class Cloud(pygame.sprite.Sprite):
    """Cloud for background"""

    def __init__(self):
        super().__init__(cloud_group)

        self.image = pygame.transform.scale(load_image('cloud.png'), (250, 100))
        self.rect = self.image.get_rect()

        self.rect.x = WIDTH + random.randint(50, WIDTH)
        self.rect.y = choice(range(50, HEIGHT // 2))

    def update(self):
        if not pause:
            self.rect.x -= CLOUD_SPEED
            if self.rect.right < 0:
                self.rect.x = WIDTH + random.randint(50, WIDTH)
                self.rect.y = choice(range(50, HEIGHT // 2))


class Dino(pygame.sprite.Sprite):
    """Main character"""

    run = [load_image('dino_run_1.png'),
           load_image('dino_run_2.png')]

    duck = [load_image('dino_duck_1.png'),
            load_image('dino_duck_2.png')]

    jump = [load_image('dino_jump.png')]

    def __init__(self):
        super().__init__(player_group)

        self.jump = False
        self.image = Dino.run[0]

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = X_STAY
        self.rect.y = Y_STAY

        self.frames = 0
        self.jump_velocity = VELOCITY

    def update(self):
        if not pause:
            self.frames = (self.frames + 1) % (FPS // 2)

            if self.jump:
                self.dino_jump()

            if (pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]) \
                    and not self.jump:
                self.jump = True

            elif (pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]) \
                    and not self.jump:
                self.dino_duck()

            elif not ((pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[
                pygame.K_s]) or self.jump):
                self.dino_run()

    def dino_run(self):
        self.image = Dino.run[self.frames // ((FPS // 2) // len(Dino.run))]

        self.rect.x = X_STAY
        self.rect.y = Y_STAY

    def dino_duck(self):
        self.image = Dino.duck[self.frames // ((FPS // 2) // len(Dino.duck))]

        self.rect.x = X_STAY
        self.rect.y = Y_DUCK

    def dino_jump(self):
        self.image = Dino.jump[0]

        if self.jump:
            self.rect.y -= self.jump_velocity * 4
            self.jump_velocity -= 1

        if self.jump_velocity < -VELOCITY:
            self.jump = False
            self.jump_velocity = VELOCITY

            # update coordinates if duck was pressed
            self.rect.x = X_STAY
            self.rect.y = Y_STAY


class Cactus(pygame.sprite.Sprite):
    """Cactus enemies"""

    def __init__(self):
        super().__init__(cactus_group)

        self.image = load_image(f"cactus_{choice(('3', '2', '1'))}.png")

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.left = WIDTH + random.randint(0, WIDTH // 2)
        self.rect.bottom = HEIGHT - 100

    def update(self):
        global pause

        if not pause:
            if not pygame.sprite.collide_mask(self, player):
                if self.rect.right > 0:
                    self.rect.x -= ENEMY_SPEED
                else:
                    self.kill()
            else:
                if not pause:
                    pause = True
                    game_over_screen()


class Ptero(pygame.sprite.Sprite):
    """Ptero enemies"""

    fly = [load_image('bird_fly_1.png'),
           load_image('bird_fly_2.png')]

    def __init__(self):
        super().__init__(ptero_group)

        self.image = Ptero.fly[0]
        self.frames = 0

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.left = WIDTH + random.randint(WIDTH // 2 + 140, WIDTH)
        self.rect.bottom = choice((ENEMY_POS, ENEMY_POS - 100))

    def update(self):
        global pause

        if not pause:
            self.frames = (self.frames + 1) % (FPS // 2)
            self.image = Ptero.fly[self.frames // ((FPS // 2) // len(Ptero.fly))]

            if not pygame.sprite.collide_mask(self, player):
                if self.rect.right > 0:
                    self.rect.x -= ENEMY_SPEED
                else:
                    self.kill()
            else:
                if not pause:
                    pause = True
                    game_over_screen()


def spawn():
    if not pause:
        rareness = 65
        if len(cloud_group) < 2 and randrange(rareness) == 14:
            Cloud()

        if len(cactus_group) < 1 and len(ptero_group) < 1 and randrange(rareness) == 14:
            Cactus()
            Ptero()


def new_game():
    global pause, score, max_score
    pause = False

    if score > max_score:
        max_score = score
        with open('records.txt', mode='a') as file:
            file.write(str(max_score // 100) + '\n')

    score = 0
    cloud_group.empty()
    cactus_group.empty()
    ptero_group.empty()


def display_score():
    if max_score:
        draw_text('MAX: ' + str(max_score // 100), screen, [WIDTH // 2, 100], 40,
                  GREY, FONT, centered=True)
        draw_text(str(score // 100), screen, [WIDTH // 2, 150], 40, GREY, FONT,
                  centered=True)
    else:
        draw_text(str(score // 100), screen, [WIDTH // 2, 150], 40, GREY, FONT,
                  centered=True)


def start_screen():
    screen.fill(WHITE)

    with open('records.txt', mode='r') as file:
        records = file.readlines()
        all_records = [int(i.rstrip()) for i in records]

        if len(all_records) != 0:
            draw_text('BEST SCORE: ' + str(max(all_records)), screen, [WIDTH // 2, HEIGHT // 2], 40,
                      GREY, FONT, centered=True)

    draw_text('DINO RUN', screen, [WIDTH // 2, HEIGHT // 4], 40, GREY, FONT,
              centered=True)
    draw_text('PRESS SPACE TO START', screen, [WIDTH // 2, HEIGHT // 2 + 50], 40, GREY, FONT,
              centered=True)

    screen.blit(load_image('dino_run_1.png'), (WIDTH // 2 - 50, HEIGHT // 3 - 10))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen():
    draw_text('GAME OVER', screen, [WIDTH // 2, HEIGHT // 4], 40, GREY, FONT,
              centered=True)
    draw_text('PRESS SPACE TO RESTART', screen, [WIDTH // 2, HEIGHT // 3], 40, GREY, FONT,
              centered=True)

    screen.blit(load_image('restart.png'), (WIDTH // 2 - 40, HEIGHT // 3 + 40))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    new_game()
                    return

        pygame.display.flip()
        clock.tick(FPS)


background = Ground()

cloud_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()
player = Dino()

cactus_group = pygame.sprite.Group()
ptero_group = pygame.sprite.Group()

score = 0
max_score = 0
pause = False

start_screen()

running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    spawn()

    background.draw()
    background.update()

    cloud_group.draw(screen)
    cloud_group.update()

    player_group.draw(screen)
    player_group.update()

    cactus_group.draw(screen)
    cactus_group.update()

    ptero_group.draw(screen)
    ptero_group.update()

    score += clock.tick(FPS)
    display_score()

    pygame.display.flip()

pygame.quit()
