import pygame
import sys
import os
import math
from enum import Enum

FPS = 60
pygame.init()
pygame.display.set_caption('Жока и бока')
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
DEBUG = True
class PlayerSM(Enum):
    IDLE = 0
    WALK = 1
    ATTACK = 2
    SHIELD = 3
    ROLL = 4

class Entity(pygame.sprite.Sprite):
    def __init__(self, prev_img, x, y, all_sprites):
        super().__init__(all_sprites)
        self.img = self.load_image(prev_img)
        self.frames = self.cut_sheet(self.img, 1, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.info = ''
        self.count_frames = 0

    def load_image(self, name):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            fullname = os.path.join('data', 'notexture.png')
        image = pygame.image.load(fullname)
        return image

    def cut_sheet(self, img_name, columns, rows):
        frames = []
        self.rect = pygame.Rect(0, 0, img_name.get_width() // columns,
                                img_name.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(img_name.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        return frames

    def update(self):
        self.change_frame(self.frames, 1)
        self.count_frames += 1

    def change_frame(self, frames, speed_coef):
        self.cur_frame = round((self.cur_frame + speed_coef) % len(frames), 1)
        self.image = frames[math.trunc(self.cur_frame)]


class MovementObject(Entity):
    def __init__(self, prev_img, x, y, all_sprites):
        super().__init__(prev_img, x, y, all_sprites)
        self.MAX_SPEED = 0
        self.ACCELERATION = 0
        self.FRICTION = 0
        self.GRAVITY = 0
        self.FALL_GRAVITY = 0
        self.BOUNCE_FORCE = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.bounce_vel = 0
        self.bounce_dist = 0

    def update(self):
        super().update()
        self.move_towards()
        self.bounce_towards()

    def move_towards(self):
        if self.direction.length() != 0:
            direction = self.direction.normalize()
            self.velocity += self.ACCELERATION * direction
            if self.velocity.length() >= self.MAX_SPEED:
                self.velocity.scale_to_length(self.MAX_SPEED)
        elif self.velocity.length() != 0:
            self.velocity.scale_to_length(math.trunc(self.velocity.length() * self.FRICTION))
        self.rect = self.rect.move(self.velocity.x, self.velocity.y)

    def bounce_towards(self):
        self.rect = self.rect.move(0, self.bounce_dist)
        self.bounce_dist = self.bounce_dist + self.bounce_vel \
            if self.bounce_vel != 0 else self.bounce_dist * self.FALL_GRAVITY
        self.rect = self.rect.move(0, -self.bounce_dist)
        self.bounce_vel = math.trunc(self.bounce_vel * self.GRAVITY)

    def bounce_rotate(self, angle, speed):
        self.image = pygame.transform.rotate(self.image, math.sin(pygame.time.get_ticks() / speed) * angle)
        self.rect = self.image.get_rect().move(self.rect.x, self.rect.y)


class Player(MovementObject):
    def __init__(self, prev_img,  x, y, all_sprites):
        # загрузка анимаций
        self.idle_sheet = self.load_animation('chr-idle', 5)
        self.walk_sheet = self.load_animation('chr-walk', 5)
        self.attack_sheet = self.load_animation('chr-attack', 1)
        self.shield_sheet = self.load_animation('chr-shield', 1)
        self.roll_sheet = self.load_animation('chr-roll', 1)
        # инит
        super().__init__(prev_img, x, y, all_sprites)
        self.state = PlayerSM.IDLE
        self.MAX_SPEED = 8
        self.ACCELERATION = 2
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.particles = pygame.sprite.Group()

    def update(self):
        match self.state:
            case PlayerSM.IDLE:
                self.move_towards()
                self.attack()
                self.shield()
                self.roll()
                self.idle_animation()
            case PlayerSM.WALK:
                self.move_towards()
                self.attack()
                self.shield()
                self.roll()
                self.walk_animation()
            case PlayerSM.ROLL:
                self.roll_animation()
            case PlayerSM.ATTACK:
                self.attack_animation()
            case PlayerSM.SHIELD:
                self.shield_animation()
        self.count_frames += 1
        self.draw_shadow()
        self.particles.update()
        self.particles.draw(screen)
        self.info = self.determine_sheet()

# функции состояний
    def move_towards(self):
        self.state = PlayerSM.WALK
        self.calculate_direction()
        self.bounce_towards()
        super().move_towards()

    def attack(self):
        button = pygame.mouse.get_pressed()
        if button[0]:
            self.state = PlayerSM.ATTACK
            self.cur_frame = 0

    def shield(self):
        button = pygame.mouse.get_pressed()
        if button[2]:
            self.state = PlayerSM.SHIELD
            self.cur_frame = 0

    def roll(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.state = PlayerSM.ROLL
            self.cur_frame = 0

    def calculate_direction(self):
        key = pygame.key.get_pressed()
        up = key[pygame.K_w] or key[pygame.K_UP]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]
        self.direction = pygame.Vector2(right - left, down - up)
        if self.direction.length() == 0:
            self.state = PlayerSM.IDLE

    def mouse_degree(self):
        mouse_pos = pygame.mouse.get_pos()
        pos = (mouse_pos[0] - self.rect.x - self.rect.width // 2, mouse_pos[1] - self.rect.y - self.rect.height // 2)
        vector = pygame.math.Vector2(pos)
        if vector.length() != 0:
            vector = vector.normalize()
        return math.atan2(vector.y, vector.x) * 180 / math.pi + (360 if vector.y < 0 else 0)

    def draw_shadow(self):
        if self.count_frames % 12 == 0:
            self.particles.add(Shadow(self.image, self.rect.x, self.rect.y))

# загрузка анимаций
    def load_animation(self, base, columns):
        sheets = []
        img = self.load_image(f'{base}-right.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-down.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-left.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-left-up.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-up.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-right-up.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        return sheets

# анимации к состояниям
    def determine_sheet(self):
        ranges = [range(0, 60), range(60, 120), range(120, 180), range(180, 240), range(240, 300), range(30, 360)]
        for i in range(len(ranges)):
            if int(self.mouse_degree()) in ranges[i]:
                return i

    def idle_animation(self):
        self.change_frame(self.idle_sheet[self.determine_sheet()], 0.1)

    def walk_animation(self):
        self.change_frame(self.walk_sheet[self.determine_sheet()], 0.2)
        self.bounce_rotate(10, 100)
        if self.cur_frame == 2:
            self.bounce_vel += self.BOUNCE_FORCE

    def attack_animation(self):
        # код
        self.state = PlayerSM.IDLE
        self.cur_frame = 0

    def roll_animation(self):
        # код
        self.state = PlayerSM.IDLE
        self.cur_frame = 0

    def shield_animation(self):
        # код
        self.state = PlayerSM.IDLE
        self.cur_frame = 0


class Shadow(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img.copy()
        self.rect = self.image.get_rect().move(x, y)
        self.image.set_alpha(128)

    def update(self):
        if self.image.get_alpha() - 4 == 0:
            self.kill()
        else:
            self.image.set_alpha(self.image.get_alpha() - 4)


def terminate():

    pygame.quit()
    sys.exit()

class MenuSM(Enum):
    MENU = 0
    START = 1
    RULES = 2
    LEAVE = 3

STATE = MenuSM.MENU
def print_text(text, x, y):
    font = pygame.font.Font(None, 50)
    need_text = font.render(text, True, pygame.Color('black'))
    screen.blit(need_text, (x, y))
class Button:
    def __init__(self, width, height, x, y, message, state):
        self.width = width
        self.height = height
        self.inactive_color = 'white'
        self.active_color = 'red'
        self.x = x
        self.y = y
        self.message = message
        self.state = state

    def draw(self):
        global STATE
        pos = pygame.mouse.get_pos()
        rect = pygame.draw.rect(screen, self.inactive_color, (self.x, self.y, self.width, self.height))
        if rect.collidepoint(pos):
            rect = pygame.draw.rect(screen, self.active_color, (self.x, self.y, self.width, self.height))
        if pygame.mouse.get_pressed()[0] == 1 and rect.collidepoint(pos):
            STATE = self.state
        print_text(self.message, self.x + 60, self.y + 10)
    def update(self):
        pass



def start_screen():
    start_game_btn = Button(200, 50, 850, 400, 'start', MenuSM.START)
    leave_game_btn = Button(200, 50, 850, 470, 'leave', MenuSM.LEAVE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return

        if STATE != MenuSM.MENU:
            return

        start_game_btn.draw()
        leave_game_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)


def game():
    all_sprites = pygame.sprite.Group()
    font = pygame.font.Font(None, 30)
    player = Player('chr.png', WIDTH // 2, HEIGHT // 2, all_sprites)
    start_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
        screen.fill('red')

        all_sprites.update()

        if STATE != MenuSM.START:
            return

        if DEBUG:
            string_rendered = font.render(str(player.info), True, 'white')
            intro_rect = string_rendered.get_rect()
            intro_rect.top = player.rect.y + 50
            intro_rect.x = player.rect.x + player.rect.width // 2 - intro_rect.width // 2
            screen.blit(string_rendered, intro_rect)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    while True:
        match STATE:
            case MenuSM.MENU:
                start_screen()
            case MenuSM.START:
                game()
            case MenuSM.LEAVE:
                terminate()
