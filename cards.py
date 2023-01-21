import random
from main import print_text
import pygame
import pathlib
import os
from ObjectEntity import *


class Card(Object):
    def __init__(self, screen, prev_img, x, y, all_sprites, player, delay):
        super().__init__(screen, prev_img, x, y, all_sprites)
        self.state = random.randint(1, 4)
        self.img = pygame.transform.scale_by(self.load_image(f'card{self.state}.png'), (3, 3))
        self.rect = self.rect.move(0, delay)
        self.image = self.img
        self.velocity = 0
        self.offset = 0
        self.group = all_sprites
        self.MAX_OFFSET = 100
        self.MAX_SPEED = 150
        self.direction = 0
        self.friction = 0.6
        self.ran_over = False
        self.player = player
        self.picked = False

    def update(self):
        self.image = self.img
        cntr = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = cntr

        self.intro()

        self.outro()

    def intro(self):
        if (self.rect.y > 400 or any(self.group.sprites())) and not self.picked:
            self.direction = -1
        elif self.picked:
            self.direction = 1
        else:
            self.direction = 0
            self.ran_over = True
        self.velocity += self.direction * 35
        self.velocity *= self.friction
        if self.velocity > self.MAX_SPEED:
            self.velocity = self.MAX_SPEED
        self.rect = self.rect.move(0, self.velocity)

    def outro(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            cntr = self.rect.center
            self.image = pygame.transform.scale_by(self.image, (1.1, 1.1))
            self.rect = self.image.get_rect()
            self.rect.center = cntr
            if pygame.mouse.get_pressed()[0] and not any(self.group.sprites()):
                сhoose_card = pygame.mixer.Sound(os.path.join('data', 'choose_card.mp3'))
                сhoose_card.play()
                сhoose_card.set_volume(0.5)
                match self.state:
                    case 1:
                        self.player.WEAPON.DAMAGE += 3
                    case 2:
                        self.player.MAX_HP += 5
                        self.player.hp += 5
                    case 3:
                        self.player.MAX_SPEED += 2
                    case 4:
                        self.player.hp = self.player.MAX_HP
                self.picked = True

    def __bool__(self):
        return self.picked
