import pygame

from ObjectEntity import *


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
        self.ATTACK_DAMAGE = 5
        self.hp = self.MAX_HP
        self.STUN_TIME = 500
        self.regen_time = 5000
        self.charge_time = 500
        self.use_time = 0
        self.used_time = 0
        self.attack_time = 1000
        self.regened = True

    def update(self):
        self.position_before_colliding = self.rect
        match self.state:
            case StateMachine.IDLE:
                self.change_frame(self.anim_sheet[0 if self.calculate_target_vector().y > 0 else 1], 0.2)
                self.count_frames += 1
                self.direction = self.calculate_target_vector()
                self.walk_anim()
                self.attack()
                self.move_towards(self.MAX_SPEED, self.ACCELERATION)
            case StateMachine.ATTACK:
                self.charge_and_attack()
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
            self.direction = self.target.direction
            self.target.stop()
        elif self.target.state != StateMachine.ATTACK and self.target.state != StateMachine.STUN \
                and self.state != StateMachine.STUN:
            self.target.get_damaged(self.ATTACK_DAMAGE if self.state.ATTACK else self.CONTACT_DAMAGE)
            self.target.state = StateMachine.STUN
            if pygame.time.get_ticks() < self.target.resist_time + self.target.STUN_TIME + 20:
                self.target.direction = -self.direction
            else:
                self.target.direction = self.direction
            self.target.resist_time = pygame.time.get_ticks()
            self.velocity = pygame.math.Vector2()

    def walk_anim(self):
        self.image = pygame.transform.scale_by(self.image, (1, 1 + math.sin(pygame.time.get_ticks() / 100) * 0.2))

    def attack(self):
        self.regen_attack()
        if self.regened and self.in_front_of_target():
            self.state = StateMachine.ATTACK
            self.use_time = pygame.time.get_ticks()
            self.regened = False
            self.stop()

    def charge_and_attack(self):
        if self.use_time + self.charge_time > pygame.time.get_ticks():
            self.change_frame(self.anim_sheet[0 if self.calculate_target_vector().y > 0 else 1], 0.2)
            self.direction = self.calculate_target_vector()
        elif self.use_time + self.attack_time > pygame.time.get_ticks():
            self.move_towards(40, 20)
            self.draw_shadow(self.load_image('bubble.png'), self.rect.center, (0, 0, 0, 0), 3)
        else:
            self.state = StateMachine.IDLE
            self.used_time = pygame.time.get_ticks()

    def regen_attack(self):
        if pygame.time.get_ticks() > self.used_time + self.regen_time:
            self.regened = True
