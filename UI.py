from main import *
from Player import *

class Heart(pygame.sprite.Sprite):
    def __init__(self, player, x, y):
        super().__init__()
        self.heart = pygame.sprite.Sprite()
        self.heart.image = pygame.image.load(os.path.join('data', 'heart.png'))
        self.heart.rect = self.heart.image.get_rect()
        self.heart.rect.x = x
        self.heart.rect.y = y
        hearts = pygame.sprite.Group()
        self.player = player
        screen.blit(self.heart.image, self.heart.rect)

    def draw_hp_line(self):
        if self.player.hp < 0:
            self.player.hp = 0
        LENGTH = 300
        HEIGHT = 30
        paint = (self.player.hp / self.player.MAX_HP) * LENGTH
        big_rect = pygame.Rect(70, 10, LENGTH, HEIGHT)
        painted_rect = pygame.Rect(70, 10, paint, HEIGHT)

        pygame.draw.rect(screen, 'white', painted_rect)
        pygame.draw.rect(screen, 'black', big_rect, 2)