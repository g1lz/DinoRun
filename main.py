from settings import *
import pygame
import os
import sys

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

        self.rect1.bottom = self.rect2.bottom = HEIGHT - 200

    def draw(self):
        screen.blit(self.image1, self.rect1)
        screen.blit(self.image2, self.rect2)

    def update(self):
        if not pause:
            self.rect1.left -= BG_SPEED
            self.rect2.left -= BG_SPEED

            if self.rect1.left < -WIDTH:
                self.rect1.left = self.rect2.right

            if self.rect2.left < -WIDTH:
                self.rect2.left = self.rect1.right


background = Ground()

pause = False
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    background.draw()
    background.update()

    pygame.display.flip()

pygame.quit()
