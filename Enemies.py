import pygame

from ObjectEntity import *
from Abilities import *


class Enemy(Entity):
    def __init__(self, screen, prev_img, x, y, all_sprites, target, obstacle_level=[]):
        super().__init__(screen, prev_img, x, y, all_sprites, obstacle_level)
        self.MAX_SPEED = 8
        self.ACCELERATION = 2
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.hp = self.MAX_HP
        self.target = target
        self.CONTACT_DAMAGE = 1
        self.STUN_TIME = 500

    def update(self):
        self.position_before_colliding = self.rect
        super().update()
        if self.hp <= 0:
            self.state = StateMachine.DEATH

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

    def in_front_of_target(self):
        rect = pygame.Rect(self.rect.center, (1, 1))
        vec = self.calculate_target_vector()
        len_vec = pygame.math.Vector2(self.target.rect.centerx - self.rect.centerx,
                                      self.target.rect.centery - self.rect.centery)
        for _ in range(int(len_vec.length())):
            rect = rect.move(vec)
            for obstacle in self.obstacle_level:
                if rect.colliderect(obstacle):
                    return False
        return True

    def death_animation(self):
        self.image = pygame.transform.scale_by(self.image, (1, 0.9))
        if self.image.get_rect().height == 0:
            self.kill()


class Bleb(Enemy):
    def __init__(self, screen, prev_img, x, y, all_sprites, target, obstacle_level=[]):
        # загрузка анимаций
        self.anim_sheet = self.load_animation('bleb', 5)
        # инит
        super().__init__(screen, prev_img, x, y, all_sprites, target, obstacle_level)
        self.MAX_SPEED = 6
        self.ACCELERATION = 1
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.CONTACT_DAMAGE = 2
        self.hp = self.MAX_HP
        self.STUN_TIME = 500
        self.ATTACK = ChargeAndAttack(self)

    def update(self):
        self.position_before_colliding = self.rect
        match self.state:
            case StateMachine.IDLE:
                self.change_frame(self.anim_sheet[0 if self.calculate_target_vector().y > 0 else 1], 0.2)
                self.count_frames += 1
                self.direction = self.calculate_target_vector()
                self.walk_anim()
                self.ATTACK.update()
                self.move_towards(self.MAX_SPEED, self.ACCELERATION)
            case StateMachine.ATTACK:
                self.ATTACK.attack()
            case StateMachine.STUN:
                self.check_stun()
                self.move_towards(self.MAX_SPEED, self.ACCELERATION)
            case StateMachine.DEATH:
                self.death_animation()
        super().update()

    def load_animation(self, base, columns):
        sheets = []
        img = self.load_image(f'{base}-down.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-up.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        return sheets

    def interact(self):
        if self.state != StateMachine.STUN:
            match self.target.state:
                case StateMachine.ATTACK:
                    self.get_damaged(self.target.WEAPON.DAMAGE)
                    self.state = StateMachine.STUN
                    self.resist_time = pygame.time.get_ticks()
                    self.direction = self.target.direction
                    self.target.stop()
                case StateMachine.SHIELD:
                    self.direction = -self.direction
                    if self.state == StateMachine.ATTACK:
                        self.ATTACK.regened = False
                        self.ATTACK.used_time = pygame.time.get_ticks()
                    self.state = StateMachine.STUN
                    self.resist_time = pygame.time.get_ticks()
                case _:
                    if self.target.state != StateMachine.STUN:
                        self.target.get_damaged(
                            self.ATTACK.DAMAGE if self.state == StateMachine.ATTACK else self.CONTACT_DAMAGE)
                        self.target.state = StateMachine.STUN
                        if pygame.time.get_ticks() < self.target.resist_time + self.target.STUN_TIME + 20:
                            self.target.direction = -self.direction
                        else:
                            self.target.direction = self.direction
                        self.target.resist_time = pygame.time.get_ticks()
                        self.velocity = pygame.math.Vector2()

    def walk_anim(self):
        self.image = pygame.transform.scale_by(self.image, (1, 1 + math.sin(pygame.time.get_ticks() / 100) * 0.2))
