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
        self.change_frame(self.frames, 1)
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


class Player(MovementObject):
    def __init__(self, prev_img,  x, y, all_sprites):
        # загрузка анимаций
        idle_img = self.load_image('chr.png')
        self.idle_sheet = self.cut_sheet(idle_img, 1, 1)
        walk_img = self.load_image('chr-walk.png')
        self.walk_sheet = self.cut_sheet(walk_img, 5, 1)
        attack_img = self.load_image('')
        self.attack_sheet = self.cut_sheet(attack_img, 1, 1)
        shield_img = self.load_image('')
        self.shield_sheet = self.cut_sheet(shield_img, 1, 1)
        roll_img = self.load_image('')
        self.roll_sheet = self.cut_sheet(roll_img, 1, 1)
        # инит
        super().__init__(prev_img, x, y, all_sprites)
        self.state = PlayerSM.IDLE
        self.MAX_SPEED = 8
        self.ACCELERATION = 2
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4

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
        self.info = self.rect

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
            self.cur_frame = 0

    def mouse_degree(self):
        mouse_pos = pygame.mouse.get_pos()
        pos = (mouse_pos[0] - self.rect.x - self.rect.width // 2, mouse_pos[1] - self.rect.y - self.rect.height // 2)
        vector = pygame.math.Vector2(pos)
        if vector.length() != 0:
            vector = vector.normalize()
        return math.atan2(vector.y, vector.x) * 180 / math.pi + (360 if vector.y < 0 else 0)

# анимации к состояниям
    def idle_animation(self):
        self.change_frame(self.idle_sheet, 1)

    def walk_animation(self):
        self.change_frame(self.walk_sheet, 0.2)
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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    screen.fill('black')
    font = pygame.font.Font(None, 50)
    text_coord = 50

    play_string_rendered = font.render('play', True, pygame.Color('black'))
    play_intro_rect = play_string_rendered.get_rect()
    play_intro_rect.x = 890
    play_intro_rect.y = 400

    rules_string_rendered = font.render('rules', True, pygame.Color('black'))
    rules_intro_rect = play_string_rendered.get_rect()
    rules_intro_rect.x = 890
    rules_intro_rect.y = 450

    leave_string_rendered = font.render('leave', True, pygame.Color('black'))
    leave_intro_rect = play_string_rendered.get_rect()
    leave_intro_rect.x = 890
    leave_intro_rect.y = 500

    while True:
        if play_intro_rect.x <= pygame.mouse.get_pos()[0] <= play_intro_rect.x + 140 and play_intro_rect.y <= \
                pygame.mouse.get_pos()[1] <= play_intro_rect.y + 40:
            pygame.draw.rect(screen, 'red', [play_intro_rect.x, play_intro_rect.y, 140, 40])
        else:
            pygame.draw.rect(screen, 'white', [play_intro_rect.x, play_intro_rect.y, 140, 40])
        screen.blit(play_string_rendered, (play_intro_rect.x + 40, play_intro_rect.y))
        if rules_intro_rect.x <= pygame.mouse.get_pos()[0] <= rules_intro_rect.x + 140 and rules_intro_rect.y <= \
                pygame.mouse.get_pos()[1] <= rules_intro_rect.y + 40:
            pygame.draw.rect(screen, 'red', [rules_intro_rect.x, rules_intro_rect.y, 140, 40])
        else:
            pygame.draw.rect(screen, 'white', [rules_intro_rect.x, rules_intro_rect.y, 140, 40])
        screen.blit(rules_string_rendered, (rules_intro_rect.x + 30, rules_intro_rect.y))
        if leave_intro_rect.x <= pygame.mouse.get_pos()[0] <= leave_intro_rect.x + 140 and leave_intro_rect.y <= \
                pygame.mouse.get_pos()[1] <= leave_intro_rect.y + 40:
            pygame.draw.rect(screen, 'red', [leave_intro_rect.x, leave_intro_rect.y, 140, 40])
        else:
            pygame.draw.rect(screen, 'white', [leave_intro_rect.x, leave_intro_rect.y, 140, 40])
        screen.blit(leave_string_rendered, (leave_intro_rect.x + 30, leave_intro_rect.y))
        pygame.display.update()
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
    player = Player('chr.png', WIDTH // 2, HEIGHT // 2, all_sprites)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
        screen.fill('black')

        all_sprites.update()

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
    start_screen()
    game()

