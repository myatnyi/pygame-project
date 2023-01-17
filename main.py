import sys
from Player import *
from Enemies import *
from Levels import *
from UI import *

FPS = 60
pygame.init()
pygame.display.set_caption('Жока и бока')
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
DEBUG = True


class MenuSM(Enum):
    MENU = 0
    START = 1
    RULES = 2
    LEAVE = 3


STATE = MenuSM.MENU


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
        self.screen = screen

    def draw(self):
        global STATE
        pos = pygame.mouse.get_pos()
        rect = pygame.draw.rect(self.screen, self.inactive_color, (self.x, self.y, self.width, self.height))
        if rect.collidepoint(pos):
            rect = pygame.draw.rect(self.screen, self.active_color, (self.x, self.y, self.width, self.height))
        if pygame.mouse.get_pressed()[0] == 1 and rect.collidepoint(pos):
            STATE = self.state
        print_text(self.message, self.x + 60, self.y + 10)


def print_text(text, x, y):
    font = pygame.font.Font(None, 50)
    need_text = font.render(text, True, pygame.Color('black'))
    screen.blit(need_text, (x, y))


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
    level = Level(screen, 'level1.txt')
    player = Player(screen, 'chr.png', WIDTH // 2, HEIGHT // 2, all_sprites, obstacle_level=level.read_file()[1])
    bleb = Bleb(screen, 'bleb.png', 400, 400, all_sprites, player, obstacle_level=level.read_file()[1])
    enemies.add(bleb)
    player.get_inter_objs(enemies)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()

        screen.fill('red')
        level.draw_border(level.read_file()[0])
        all_sprites.update()
        Heart(player)

        if STATE != MenuSM.START:
            return

        if DEBUG:
            string_rendered = font.render(str(player.info), True, 'white')
            intro_rect = string_rendered.get_rect()
            intro_rect.top = player.rect.y + 50
            intro_rect.x = player.rect.x + player.rect.width // 2 - intro_rect.width // 2
            screen.blit(string_rendered, intro_rect)
        all_sprites.draw(screen)
        Heart(player).draw_hp_line()
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    while True:
        match STATE:
            case MenuSM.MENU:
                start_screen()
            case MenuSM.START:
                game()
            case MenuSM.LEAVE:
                terminate()
