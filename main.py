import sys
import random
from Player import *
from Enemies import *
from Levels import *
from UI import *
from ObjectEntity import *

FPS = 60
pygame.init()
pygame.display.set_caption('Жока и бока')
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
clock = pygame.time.Clock()
DEBUG = True

class Star(Object):
    def __init__(self, screen, prev_img, x, y, all_sprites):
        super().__init__(screen, prev_img, x, y, all_sprites)
        self.img = self.load_image(prev_img)
        self.cur_frame = random.randrange(0, 3)
        self.count_frames = 0
        self.frames = self.cut_sheet(self.img, 2, 2)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def update(self):
        self.change_frame(self.frames, 0.1)
        self.count_frames += 1

class Background():
    def __init__(self):
        super().__init__()
        self.stars = []
        for i in range(300):
            self.stars.append((random.randrange(0, 1800), random.randrange(0, 1920)))
        self.stars_group = pygame.sprite.Group()
        for i in range(len(self.stars)):
            star = Star(screen, 'star.png', self.stars[i][0], self.stars[i][1], self.stars_group)
    def update(self):
        self.stars_group.update()
        self.stars_group.draw(screen)


class MenuSM(Enum):
    MENU = 0
    START = 1
    RULES = 2
    LEAVE = 3
    FINAL = 4


STATE = MenuSM.MENU


class Button:
    def __init__(self, width, height, x, y, message, state, size_text):
        self.width = width
        self.height = height
        self.inactive_color = 'white'
        self.active_color = 'red'
        self.x = x
        self.y = y
        self.message = message
        self.state = state
        self.screen = screen
        self.size_text = size_text

    def draw(self):
        global STATE
        pos = pygame.mouse.get_pos()
        rect = pygame.draw.rect(self.screen, self.inactive_color, (self.x, self.y, self.width, self.height))
        if rect.collidepoint(pos):
            rect = pygame.draw.rect(self.screen, self.active_color, (self.x, self.y, self.width, self.height))
            print_text(f'>>{self.message}<<', self.x, self.y + 10, 'black', self.size_text)
        else:
            print_text(self.message, self.x + 50, self.y + 10, 'black', self.size_text)
        if pygame.mouse.get_pressed()[0] == 1 and rect.collidepoint(pos):
            STATE = self.state




def print_text(text, x, y, color, size):
    font = pygame.font.Font(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'cool_font.ttf'), size)
    need_text = font.render(text, True, pygame.Color(color))
    screen.blit(need_text, (x, y))


def start_screen():
    start_game_btn = Button(200, 50, 850, 400, 'start', MenuSM.START, 30)
    leave_game_btn = Button(200, 50, 850, 470, 'leave', MenuSM.LEAVE, 30)
    print_text('start game!', 800, 320, 'white', 50)
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


KILLS = 0
TIME = 0
SCORE = 0
def final_screen():
    screen.fill('black')
    restart_game_btn = Button(200, 50, 850, 500, 'restart', MenuSM.START, 30)
    leave_game_btn = Button(200, 50, 850, 570, 'leave', MenuSM.LEAVE, 30)
    print_text('you lose(', 800, 150, 'white', 120)
    print_text(f'kills: {KILLS}', 840, 260, 'white', 70)
    print_text(f'time: {TIME}', 840, 320, 'white', 70)
    print_text(f'score: {SCORE}', 840, 380, 'white', 70)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return

        if STATE != MenuSM.FINAL:
            return

        restart_game_btn.draw()
        leave_game_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)


def game():
    global STATE
    all_sprites = pygame.sprite.Group()
    font = pygame.font.Font(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'cool_font.ttf'), 30)
    enemies = pygame.sprite.Group()
    level = Level(screen, 'level1.txt')
    player = Player(screen, 'chr.png', WIDTH // 2, HEIGHT // 2, all_sprites, obstacle_level=level.read_file()[1])
    bleb = Bleb(screen, 'bleb.png', 400, 400, all_sprites, player, obstacle_level=level.read_file()[1])
    enemies.add(bleb)
    player.get_inter_objs(enemies)
    bg = Background()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                STATE = MenuSM.MENU
                start_screen()

        screen.fill('black')
        all_sprites.update()
        Heart(player, 20, 7)
        bg.update()
        level.draw_border(level.read_file()[0])

        if STATE != MenuSM.START:
            return

        if player.hp <= 0:
            STATE = MenuSM.FINAL
            return

        if DEBUG:
            string_rendered = font.render(str(player.info), True, 'white')
            intro_rect = string_rendered.get_rect()
            intro_rect.top = player.rect.y + 50
            intro_rect.x = player.rect.x + player.rect.width // 2 - intro_rect.width // 2
            screen.blit(string_rendered, intro_rect)
        all_sprites.draw(screen)
        Heart(player, 20, 7).draw_hp_line()
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
            case MenuSM.FINAL:
                final_screen()
