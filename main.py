import pygame
import sys
import os
import math

FPS = 50
pygame.init()
pygame.display.set_caption('Жока и бока')
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

DEBUG = True


class Entity(pygame.sprite.Sprite):
    def __init__(self, img_name, columns, rows, x, y, all_sprites):
        super().__init__(all_sprites)
        self.frames = []
        self.img = self.load_image(img_name)
        self.cut_sheet(self.img, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def load_image(self, name):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            fullname = os.path.join('data', 'notexture.png')
        image = pygame.image.load(fullname)
        return image

    def cut_sheet(self, img_name, columns, rows):
        self.rect = pygame.Rect(0, 0, img_name.get_width() // columns,
                                img_name.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(img_name.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class MovementObject(Entity):
    def __init__(self, img_name, columns, rows, x, y, all_sprites):
        super().__init__(img_name, columns, rows, x, y, all_sprites)
        self.MAX_SPEED = 50
        self.ACCELERATION = 5
        self.FRICTION = 0.9
        self.direction = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)

    def update(self):
        super().update()
        if self.direction.length() != 0:
            direction = self.direction.normalize()
            self.velocity += self.ACCELERATION * direction
            if self.velocity.length() >= self.MAX_SPEED:
                self.velocity.scale_to_length(self.MAX_SPEED)
        elif self.velocity.length() != 0:
            self.velocity.scale_to_length(math.trunc(self.velocity.length() * self.FRICTION))
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y


class Player(MovementObject):
    def __init__(self, img_name, columns, rows, x, y, all_sprites):
        super().__init__(img_name, columns, rows, x, y, all_sprites)

    def update(self):
        key = pygame.key.get_pressed()
        up = key[pygame.K_w] or key[pygame.K_UP]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]
        self.direction = pygame.Vector2(right - left, down - up)
        super().update()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["типа меню", "",
                  "типа кнопка",
                  "да",
                  "нет"]

    screen.fill('blue')
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def game():
    all_sprites = pygame.sprite.Group()
    font = pygame.font.Font(None, 30)
    player = Player('chr.png', 1, 1, WIDTH // 2, HEIGHT // 2, all_sprites)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
        screen.fill('black')

        all_sprites.update()

        if DEBUG:
            string_rendered = font.render(str(player.rect), True, 'white')
            intro_rect = string_rendered.get_rect()
            intro_rect.top = player.rect.y + 50
            intro_rect.x = player.rect.x - intro_rect.width // 2
            screen.blit(string_rendered, intro_rect)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    start_screen()
    game()

