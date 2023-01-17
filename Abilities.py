import pygame
from statemachine import *


class Ability:
    def __init__(self, owner):
        self.owner = owner
        self.regen_time = 0
        self.charge_time = 0
        self.use_time = 0
        self.used_time = 0
        self.attack_time = 0
        self.regened = True
        self.DAMAGE = 0

    def update(self):
        if pygame.time.get_ticks() > self.used_time + self.regen_time and not self.regened:
            self.regened = True
        if self.regened and self.owner.in_front_of_target():
            self.owner.state = StateMachine.ATTACK
            self.use_time = pygame.time.get_ticks()
            self.regened = False
            self.owner.stop()

    def attack(self):
        pass


class ChargeAndAttack(Ability):
    def __init__(self, owner):
        super().__init__(owner)
        self.regen_time = 5000
        self.charge_time = 500
        self.attack_time = 1000
        self.DAMAGE = 5

    def attack(self):
        if self.use_time + self.charge_time > pygame.time.get_ticks():
            self.owner.change_frame(self.owner.anim_sheet[0 if self.owner.calculate_target_vector().y > 0 else 1], 0.2)
            self.owner.direction = self.owner.calculate_target_vector()
        elif self.use_time + self.attack_time > pygame.time.get_ticks():
            self.owner.move_towards(40, 20)
            self.owner.draw_shadow(self.owner.load_image('bubble.png'), self.owner.rect.center, (0, 0, 0, 0), 3)
        else:
            self.owner.state = StateMachine.IDLE
            self.used_time = pygame.time.get_ticks()


class Weapon(Ability):
    def __init__(self, owner):
        super().__init__(owner)
        self.regen_time = 1000
        self.charge_time = 0
        self.attack_time = 0
        self.DAMAGE = 3

    def attack(self):
        self.owner.draw_shadow(self.owner.image, self.owner.rect, (255, 0, 0, 128), 4)
        self.owner.change_frame(self.owner.attack_sheet[self.owner.determine_sheet()],
                                0.1 if 2 <= self.owner.cur_frame < 4 else 0.5)
        if self.owner.cur_frame < 3:
            self.owner.move_towards(8, 4)
        else:
            self.owner.move_towards(2, 1)
        if self.owner.cur_frame == 4:
            self.owner.state = StateMachine.IDLE