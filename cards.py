import random
from main import print_text
import pygame
import pathlib
import os
from ObjectEntity import *


class Card(Object):
    def __init__(self, screen, prev_img, x, y, all_sprites, player):
        super().__init__(screen, prev_img, x, y, all_sprites)
        self.velocity = 0
        self.offset = 0
        self.MAX_OFFSET = 100
        self.MAX_SPEED = 30
        self.direction = 0
        self.friction = 0.6
        self.ran_over = False
        self.player = player
        self.state = random.randint(1, 3)
        self.picked = False

    def update(self):
        match self.state:
            case 1:
                text = '+УРОН'
            case 2:
                text = '+ХП'
            case 3:
                text = '+СКОРОСТЬ'
        super().update()
        cntr = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = cntr
        if not self.ran_over:
            self.intro()
            print_text(text, self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2, 'black', 50,
                       centered=True)
        else:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                cntr = self.rect.center
                self.image = pygame.transform.scale_by(self.image, (1.1, 1.1))
                self.rect = self.image.get_rect()
                self.rect.center = cntr
                print_text(text, self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2, 'black', 55,
                           centered=True)
                if pygame.mouse.get_pressed()[0]:
                    match self.state:
                        case 1:
                            self.player.WEAPON.DAMAGE += 3
                        case 2:
                            self.player.MAX_HP += 5
                            self.player.hp += 5
                        case 3:
                            self.player.MAX_SPEED += 2
                    self.picked = True
            else:
                print_text(text, self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2, 'black', 50,
                           centered=True)


    def intro(self):
        if self.rect.y > 300:
            self.direction = -1
        else:
            self.direction = 0
            self.ran_over = True
        if self.velocity > self.MAX_SPEED:
            self.velocity = self.MAX_SPEED
        self.velocity += self.direction * 30
        self.velocity *= self.friction
        self.rect = self.rect.move(0, self.velocity)

    def __bool__(self):
        return self.picked
