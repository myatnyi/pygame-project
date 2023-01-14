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
DEBUG = False


class Level:
    def __init__(self, filename):
        self.filename = filename

    def read_file(self):
        lines = []
        with open(os.path.join(os.getcwd(), 'levels', self.filename), 'r') as file:
            list_coords = []
            with open(os.path.join(os.getcwd(), 'levels', self.filename), 'r') as file:
                for line in file.readlines():
                    coords = [int(num) for num in line.split()]
                    list_coords.append(coords)
                for i in range(len(list_coords)):
                    if list_coords[i] == list_coords[-1]:
                        lines.append(pygame.draw.line(screen, 'white', list_coords[i], list_coords[0], 10))
                    else:
                        lines.append(pygame.draw.line(screen, 'white', list_coords[i], list_coords[i + 1], 10))

            return list_coords, lines


    def draw_border(self, coords):
        border = pygame.draw.lines(screen, 'white', True, coords, 10)
        pygame.draw.polygon(screen, 'black', coords)

Level('level1.txt').read_file()
class StateMachine(Enum):
    IDLE = 0
    WALK = 1
    ATTACK = 2
    SHIELD = 3
    ROLL = 4
    STUN = 5


class Object(pygame.sprite.Sprite):
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
            fullname = os.path.join(os.getcwd(), 'data', 'notexture.png')
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


class Entity(Object):
    def __init__(self, prev_img, x, y, all_sprites, obstacle_level=[]):
        super().__init__(prev_img, x, y, all_sprites)
        self.MAX_SPEED = 0
        self.ACCELERATION = 0
        self.FRICTION = 0
        self.GRAVITY = 0
        self.FALL_GRAVITY = 0
        self.BOUNCE_FORCE = 0
        self.MAX_HP = 0
        self.state = StateMachine.IDLE
        self.hp = 0
        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.bounce_vel = 0
        self.bounce_dist = 0
        self.resist_time = 0
        self.obstacle_level = obstacle_level
        self.position_before_colliding = self.rect
        self.particles = pygame.sprite.Group()
        self.walk_hitbox = pygame.Rect(self.rect.x, self.rect.y + self.rect.height * 0.7,
                                       self.rect.width, self.rect.height * 0.3)

    def update(self):
        self.collision_interact()
        if self.state == StateMachine.STUN:
            self.blink()
        self.particles.update()
        self.particles.draw(screen)

    def move_towards(self, max_speed, acceleration):
        if self.direction.length() != 0:
            direction = self.direction.normalize()
            self.velocity += acceleration * direction
            if self.velocity.length() >= max_speed:
                self.velocity.scale_to_length(max_speed)
        elif self.velocity.length() != 0:
            if math.trunc(self.velocity.length() * self.FRICTION) == 0:
                self.velocity = pygame.math.Vector2()
            else:
                self.velocity.scale_to_length(math.trunc(self.velocity.length() * self.FRICTION))
        self.move_and_collide(self.velocity)

    def bounce_towards(self):
        self.rect = self.rect.move(0, self.bounce_dist)
        self.bounce_dist = self.bounce_dist + self.bounce_vel \
            if self.bounce_vel != 0 else self.bounce_dist * self.FALL_GRAVITY
        self.rect = self.rect.move(0, -self.bounce_dist)
        self.bounce_vel = math.trunc(self.bounce_vel * self.GRAVITY)

    def bounce_rotate(self, angle, speed):
        self.image = pygame.transform.rotate(self.image, math.sin(pygame.time.get_ticks() / speed) * angle)

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

    def move_and_collide(self, velocity):
        if velocity.x != 0:
            for i in range(math.trunc(abs(velocity.x))):
                self.rect = self.rect.move(int(velocity.x / abs(velocity.x)), 0)
                self.walk_hitbox = self.walk_hitbox.move(int(velocity.x / abs(velocity.x)), 0)
                for obstacle in self.obstacle_level:
                    if self.walk_hitbox.colliderect(obstacle):
                        self.rect = self.rect.move(-(int(velocity.x / abs(velocity.x))), 0)
                        self.walk_hitbox = self.walk_hitbox.move(-(int(velocity.x / abs(velocity.x))), 0)
        if velocity.y != 0:
            for i in range(math.trunc(abs(velocity.y))):
                self.rect = self.rect.move(0, int(velocity.y / abs(velocity.y)))
                self.walk_hitbox = self.walk_hitbox.move(0, int(velocity.y / abs(velocity.y)))
                for obstacle in self.obstacle_level:
                    if self.walk_hitbox.colliderect(obstacle):
                        self.rect = self.rect.move(0, -(int(velocity.y / abs(velocity.y))))
                        self.walk_hitbox = self.walk_hitbox.move(0, -(int(velocity.y / abs(velocity.y))))
        if DEBUG:
            pygame.draw.rect(screen, 'blue', (self.walk_hitbox.x, self.walk_hitbox.y, self.walk_hitbox.width,
                                              self.walk_hitbox.height))

    def collision_interact(self):
        pass

    def interact(self):
        pass

    def blink(self):
        self.image.set_alpha(int(((math.sin(pygame.time.get_ticks() / 30) + 1) / 2) * 255))

    def stop(self):
        self.velocity = pygame.math.Vector2()
        self.rect = self.position_before_colliding

    def get_damaged(self, damage):
        self.hp -= damage

    def check_stun(self):
        if pygame.time.get_ticks() - self.resist_time > 500:
            self.resist_time = 0
            self.state = StateMachine.IDLE
            self.image.set_alpha(255)


class Enemy(Entity):
    def __init__(self, prev_img, x, y, all_sprites, target, obstacle_level=[]):
        super().__init__(prev_img, x, y, all_sprites, obstacle_level)
        self.MAX_SPEED = 8
        self.ACCELERATION = 2
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.hp = self.MAX_HP
        self.target = target

    def update(self):
        self.position_before_colliding = self.rect
        super().update()
        if self.hp <= 0:
            self.kill()

    def calculate_target_vector(self):
        vector = pygame.math.Vector2(self.target.rect.x - self.rect.x, self.target.rect.y - self.rect.y)
        if vector.length() != 0:
            vector = vector.normalize()
        return vector

    def frict(self):
        if self.direction.length() != 0:
            if round(self.direction.length() * self.FRICTION, 2) != 0:
                self.direction.scale_to_length(self.direction.length() * self.FRICTION)
            else:
                self.direction = pygame.math.Vector2()


class Bleb(Enemy):
    def __init__(self, prev_img, x, y, all_sprites, target, obstacle_level=[]):
        # загрузка анимаций
        self.anim_sheet = self.load_animation('bleb', 5)
        # инит
        super().__init__(prev_img, x, y, all_sprites, target, obstacle_level)
        self.MAX_SPEED = 6
        self.ACCELERATION = 1
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.hp = self.MAX_HP

    def update(self):
        self.position_before_colliding = self.rect
        match self.state:
            case StateMachine.IDLE:
                self.change_frame(self.anim_sheet[0 if self.calculate_target_vector().y > 0 else 1], 0.2)
                self.count_frames += 1
                self.direction = self.calculate_target_vector()
            case StateMachine.STUN:
                self.check_stun()
        self.move_towards(self.MAX_SPEED, self.ACCELERATION)
        if self.hp <= 0:
            self.kill()
        super().update()

    def load_animation(self, base, columns):
        sheets = []
        img = self.load_image(f'{base}-down.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-up.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        return sheets

    def interact(self):
        if self.target.state == StateMachine.ATTACK and self.state != StateMachine.STUN:
            self.get_damaged(1)
            self.state = StateMachine.STUN
            self.resist_time = pygame.time.get_ticks()
            self.direction = pygame.math.Vector2(self.target.direction.x, self.target.direction.y)
        elif self.target.state != StateMachine.ATTACK and self.target.state != StateMachine.STUN:
            self.target.get_damaged(1)
            self.target.state = StateMachine.STUN
            self.target.direction = pygame.math.Vector2(self.direction.x, self.direction.y)
            self.velocity = pygame.math.Vector2()


class Player(Entity):
    def __init__(self, prev_img, x, y, all_sprites, obstacle_level=[]):
        # загрузка анимаций
        self.idle_sheet = self.load_animation('chr-idle', 5)
        self.walk_sheet = self.load_animation('chr-walk', 5)
        self.attack_sheet = self.load_animation('chr-attack', 5)
        self.shield_sheet = self.load_animation('chr-shield', 1)
        self.roll_sheet = self.load_animation('chr-roll', 1)
        dead_img = self.load_image(f'chr-dead')
        self.dead_sheet = self.cut_sheet(dead_img, 1, 1)
        # инит
        super().__init__(prev_img, x, y, all_sprites, obstacle_level)
        self.state = StateMachine.IDLE
        self.MAX_SPEED = 8
        self.ACCELERATION = 2
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.hp = self.MAX_HP
        self.inter_objs = []

    def update(self):
        previous_state = self.state
        self.position_before_colliding = self.rect
        match self.state:
            case StateMachine.IDLE:
                self.walk_towards()
                self.attack()
                self.shield()
                self.roll()
                self.idle_animation()
            case StateMachine.WALK:
                self.walk_towards()
                self.attack()
                self.shield()
                self.roll()
                self.walk_animation()
            case StateMachine.ROLL:
                self.roll_animation()
            case StateMachine.ATTACK:
                self.attack_animation()
            case StateMachine.SHIELD:
                self.shield_animation()
            case StateMachine.STUN:
                self.check_stun()
                self.move_towards(200, 20)
        if previous_state != self.state:
            self.cur_frame = 0
        if self.hp <= 0:
            self.death_animation()
        self.count_frames += 1
        super().update()
        self.info = self.hp

# функции состояний
    def walk_towards(self):
        self.state = StateMachine.WALK
        self.calculate_direction()
        self.move_towards(self.MAX_SPEED, self.ACCELERATION)
        self.bounce_towards()

    def attack(self):
        button = pygame.mouse.get_pressed()
        if button[0]:
            self.direction = self.mouse_vector()
            self.state = StateMachine.ATTACK

    def shield(self):
        button = pygame.mouse.get_pressed()
        if button[2]:
            self.state = StateMachine.SHIELD

    def roll(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.state = StateMachine.ROLL

    def calculate_direction(self):
        key = pygame.key.get_pressed()
        up = key[pygame.K_w] or key[pygame.K_UP]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]
        self.direction = pygame.Vector2(right - left, down - up)
        if self.direction.length() == 0:
            self.state = StateMachine.IDLE

    def mouse_vector(self):
        mouse_pos = pygame.mouse.get_pos()
        pos = (mouse_pos[0] - self.rect.x - self.rect.width // 2, mouse_pos[1] - self.rect.y - self.rect.height // 2)
        vector = pygame.math.Vector2(pos)
        if vector.length() != 0:
            vector = vector.normalize()
        return vector

    def mouse_degree(self):
        vector = self.mouse_vector()
        return math.atan2(vector.y, vector.x) * 180 / math.pi + (360 if vector.y < 0 else 0)

    def draw_shadow(self):
        self.particles.add(Shadow(self.image, self.rect.x, self.rect.y))

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
        self.draw_shadow()
        self.change_frame(self.attack_sheet[self.determine_sheet()], 0.1 if 2 <= self.cur_frame < 4 else 0.5)
        if self.cur_frame < 3:
            self.move_towards(8, 4)
        else:
            self.move_towards(2, 1)
        if self.cur_frame == 4:
            self.state = StateMachine.IDLE

    def roll_animation(self):
        # код
        self.state = StateMachine.IDLE
        self.cur_frame = 0

    def shield_animation(self):
        # код
        self.state = StateMachine.IDLE
        self.cur_frame = 0

    def death_animation(self):
        self.kill()

    def collision_interact(self):
        for group in self.inter_objs:
            for inter in pygame.sprite.spritecollide(self, group, False, pygame.sprite.collide_mask):
                inter.interact()

    def get_inter_objs(self, *inter_objs):
        self.inter_objs = inter_objs


class Shadow(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img.copy()
        self.rect = self.image.get_rect().move(x, y)
        self.color_rect = pygame.mask.from_surface(self.image)
        # вариант 1
        # self.color = pygame.Color(255, pygame.time.get_ticks() % 255, pygame.time.get_ticks() % 255, 128)
        # вариант 2
        # self.color = pygame.Color(pygame.time.get_ticks() % 255, 0, 0, 128)
        # вариант 3
        # hsv = self.color.hsva
        # self.color.hsva = (pygame.time.get_ticks() % 360, 75, 100, 50)
        # не вариант
        self.color = pygame.Color(255, 0, 0, 128)
        self.image.set_alpha(128)

    def update(self):
        if self.image.get_alpha() - 4 == 0:
            self.kill()
        else:
            screen.blit(self.color_rect.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=self.color), self.rect)
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
    enemies = pygame.sprite.Group()
    level = Level('level3.txt')
    player = Player('chr.png', WIDTH // 2, HEIGHT // 2, all_sprites)
    bleb = Bleb('', 400, 400, all_sprites, player)
    enemies.add(bleb)
    player.get_inter_objs(enemies)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()

        screen.fill('red')
        level.draw_border(level.read_file()[0])
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
