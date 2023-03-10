from main import *
from Player import *

class Heart(pygame.sprite.Sprite):
    def __init__(self, player, x, y):
        super().__init__()
        self.heart = pygame.sprite.Sprite()
        self.heart.image = pygame.image.load(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'heart.png'))
        self.heart.rect = self.heart.image.get_rect()
        self.heart.rect.x = x
        self.heart.rect.y = y
        hearts = pygame.sprite.Group()
        self.player = player

    def draw_hp_line(self, screen):
        if self.player.hp < 0:
            self.player.hp = 0
        LENGTH = 300
        HEIGHT = 30
        paint = (self.player.hp / self.player.MAX_HP) * LENGTH
        big_rect = pygame.Rect(70, 10, LENGTH, HEIGHT)
        painted_rect = pygame.Rect(70, 10, paint, HEIGHT)
        screen.blit(self.heart.image, self.heart.rect)
        pygame.draw.rect(screen, (137, 23, 48), painted_rect)
        pygame.draw.rect(screen, 'white', big_rect, 2)