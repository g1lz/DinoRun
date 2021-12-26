from settings import *
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


class Ground:
    """Ground for background"""

    def __init__(self):
        self.image1 = pygame.transform.scale(load_image('ground.png'), (WIDTH, 20))
        self.rect1 = self.image1.get_rect()
        self.rect1.left = 0

        self.image2 = pygame.transform.scale(load_image('ground.png'), (WIDTH, 20))
        self.rect2 = self.image2.get_rect()
        self.rect2.left = WIDTH

        self.rect1.bottom = self.rect2.bottom = 600

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

        self.rect.left = WIDTH + random.randint(50, WIDTH)
        self.rect.top = random.randint(50, HEIGHT // 2)

    def update(self):
        if not pause:
            self.rect.left -= CLOUD_SPEED
            if self.rect.right < 0:
                self.rect.left = WIDTH + random.randint(50, WIDTH)
                self.rect.top = random.randint(50, HEIGHT // 2)


class Dino(pygame.sprite.Sprite):
    """Main character"""

    run = [pygame.transform.scale(load_image('dino_run_1.png'), (100, 100)),
           pygame.transform.scale(load_image('dino_run_2.png'), (100, 100))]

    duck = [pygame.transform.scale(load_image('dino_duck_1.png'), (120, 100)),
            pygame.transform.scale(load_image('dino_duck_2.png'), (120, 100))]

    def __init__(self):
        super().__init__(player_group)

        self.frames = 0

        self.image = Dino.run[self.frames]
        self.rect = self.image.get_rect(center=(150, 550))

    def gravity(self):
        if self.rect.centery <= 550:
            self.rect.centery += GRAVITY

    def update(self):
        self.gravity()

        if not pause:
            pic_ind = self.frames // (FPS * 4 // len(Dino.run))
            self.image = Dino.run[pic_ind]
            self.frames = (self.frames + 1) % (FPS * 4)

            if pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]:
                self.image = Dino.duck[pic_ind]

            if pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w] or \
                    pygame.key.get_pressed()[pygame.K_SPACE]:
                if self.rect.centery >= 550:
                    while self.rect.centery - VELOCITY > 40:
                        self.rect.centery -= 1


background = Ground()

cloud_group = pygame.sprite.Group()
for i in range(1, 4):
    Cloud()

player_group = pygame.sprite.Group()
player = Dino()

pause = False
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    background.draw()
    background.update()

    cloud_group.draw(screen)
    cloud_group.update()

    player_group.draw(screen)
    player_group.update()

    pygame.display.flip()

pygame.quit()
