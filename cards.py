import pygame
import pathlib
import os
from ObjectEntity import *


class Card(Object):
    def __init__(self, screen, prev_img, x, y, all_sprites):
        super().__init__(screen, prev_img, x, y, all_sprites)
        self.velocity = 0
        self.offset = 0
        self.MAX_OFFSET = 100
        self.MAX_SPEED = 30
        self.direction = 0
        self.friction = 0.6
        self.ran_over = False

    def update(self):
        super().update()
        cntr = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = cntr
        if not self.ran_over:
            self.intro()
        else:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                cntr = self.rect.center
                self.image = pygame.transform.scale_by(self.image, (1.1, 1.1))
                self.rect = self.image.get_rect()
                self.rect.center = cntr


    def intro(self):
        if self.rect.y > 300:
            self.direction = -1
        else:
            self.direction = 0
            self.ran_over = True
        if self.velocity > self.MAX_SPEED:
            self.velocity = self.MAX_SPEED
        self.velocity += self.direction * 20
        self.velocity *= self.friction
        self.rect = self.rect.move(0, self.velocity)
