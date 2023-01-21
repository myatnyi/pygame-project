import pygame
import os
import pathlib
import math
from statemachine import *


class Shadow(pygame.sprite.Sprite):
    def __init__(self, screen, img, x, y, color, time):
        super().__init__()
        self.image = img.copy()
        self.rect = self.image.get_rect().move(x, y)
        self.color_rect = pygame.mask.from_surface(self.image)
        self.screen = screen
        self.time = time
        # вариант 1
        # self.color = pygame.Color(255, pygame.time.get_ticks() % 255, pygame.time.get_ticks() % 255, 128)
        # вариант 2
        # self.color = pygame.Color(pygame.time.get_ticks() % 255, 0, 0, 128)
        # вариант 3
        # hsv = self.color.hsva
        # self.color.hsva = (pygame.time.get_ticks() % 360, 75, 100, 50)
        # не вариант
        self.color = pygame.Color(color)
        self.image.set_alpha(128)

    def update(self):
        if self.image.get_alpha() - 4 <= 0:
            self.kill()
        else:
            self.screen.blit(self.color_rect.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=self.color), self.rect)
            self.image.set_alpha(self.image.get_alpha() - self.time)


class Object(pygame.sprite.Sprite):
    def __init__(self, screen, prev_img, x, y, all_sprites):
        super().__init__(all_sprites)
        self.img = self.load_image(prev_img)
        self.frames = self.cut_sheet(self.img, 1, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.info = ''
        self.count_frames = 0
        self.screen = screen

    def load_image(self, name):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            fullname = os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'notexture.png')
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
        self.cur_frame = round((self.cur_frame + speed_coef) % len(frames), 2)
        self.image = frames[math.trunc(self.cur_frame)]


class Entity(Object):
    def __init__(self, screen, prev_img, x, y, all_sprites):
        super().__init__(screen, prev_img, x, y, all_sprites)
        self.MAX_SPEED = 0
        self.ACCELERATION = 0
        self.FRICTION = 0
        self.GRAVITY = 0
        self.FALL_GRAVITY = 0
        self.BOUNCE_FORCE = 0
        self.MAX_HP = 0
        self.STUN_TIME = 500
        self.state = StateMachine.IDLE
        self.hp = 0
        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.bounce_vel = 0
        self.bounce_dist = 0
        self.resist_time = 0
        self.obstacle_level = []
        self.particles = pygame.sprite.Group()
        self.walk_hitbox = pygame.Rect((self.rect.x, self.rect.y + self.rect.height * 0.7, self.rect.width,
                                        self.rect.height * 0.3))
        self.position_before_colliding = self.rect, self.walk_hitbox

    def update(self):
        self.collision_interact()
        if self.state == StateMachine.STUN:
            self.blink()
        self.particles.update()
        self.particles.draw(self.screen)

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

    def collision_interact(self):
        pass

    def interact(self):
        pass

    def blink(self):
        self.image.set_alpha(int(((math.sin(pygame.time.get_ticks() / 30) + 1) / 2) * 255))

    def stop(self):
        self.velocity = pygame.math.Vector2()
        self.rect = self.position_before_colliding[0]
        self.walk_hitbox = self.position_before_colliding[1]

    def get_damaged(self, damage):
        self.hp -= damage
        if pygame.time.get_ticks() - self.resist_time > self.STUN_TIME:
            self.state = StateMachine.IDLE
            self.draw_shadow(self.image, self.rect, (255, 0, 0, self.image.get_alpha()), 128)

    def check_stun(self):
        if pygame.time.get_ticks() - self.resist_time > self.STUN_TIME and self.state == StateMachine.STUN:
            self.state = StateMachine.IDLE
            self.image.set_alpha(255)

    def draw_shadow(self, surf, rect, color, time):
        self.particles.add(Shadow(self.screen, surf, rect[0], rect[1], color, time))

    def load_obs(self, level):
        self.obstacle_level = level

