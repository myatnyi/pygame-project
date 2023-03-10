import os.path
import sys
import random

import pygame.draw
from cards import *
from Player import *
from Enemies import *
from Levels import *
from UI import *
from ObjectEntity import *

FPS = 60
pygame.init()
pygame.display.set_caption('Жока и бока')
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
clock = pygame.time.Clock()
DEBUG = False
FLOOR = 1
KILLS = 0
TIME = 0
SCORE = 0

pygame.mixer.music.load(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'menu_or_final.mp3'))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

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
        self.change_frame(self.frames, 0.05)
        self.count_frames += 1

class Background:
    def __init__(self, negative=False):
        self.stars = []
        for i in range(300):
            self.stars.append((random.randrange(0, 1920), (random.randrange(0, 1080))))
        self.stars_group = pygame.sprite.Group()
        for i in range(len(self.stars)):
            star = Star(screen, 'star.png' if not negative else 'star-negative.png', self.stars[i][0], self.stars[i][1],
                        self.stars_group)
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
            if pygame.mouse.get_pressed()[0]:
                get_damage_sound = pygame.mixer.Sound(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'push_btn.mp3'))
                get_damage_sound.play()
                get_damage_sound.set_volume(1)
        else:
            print_text(self.message, self.x + 50, self.y + 10, 'black', self.size_text)
        if pygame.mouse.get_pressed()[0] == 1 and rect.collidepoint(pos):
            STATE = self.state

def print_text(text, x, y, color, size, centered=False):
    font = pygame.font.Font(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'cool_font.ttf'), size)
    need_text = font.render(text, True, pygame.Color(color))
    intro_rect = need_text.get_rect()
    intro_rect.y = y - intro_rect.height // 2 if centered else y
    intro_rect.x = x - intro_rect.width // 2 if centered else x
    screen.blit(need_text, intro_rect)


def transition(color):
    expanded = False
    cube = pygame.draw.rect(screen, color, (WIDTH // 2, HEIGHT // 2, 1, 2))
    while True:
        if not expanded:
            cube = pygame.draw.rect(screen, color, ((WIDTH - cube.width) // 2, (HEIGHT - cube.height) // 2, 2,
                                                    math.ceil(cube.height * 1.1)))
            if cube.height >= HEIGHT:
                expanded = True
        else:
            cube = pygame.draw.rect(screen, color, ((WIDTH - cube.width) // 2, (HEIGHT - cube.height) // 2,
                                                    math.ceil(cube.width * 1.02), cube.height))
            if cube.width >= WIDTH:
                return
        pygame.display.flip()


def death_animation(player):
    radius = 1
    while True:
        pygame.draw.circle(screen, 'red', (player.rect.x, player.rect.y), radius)
        print(radius)
        radius = math.ceil(radius * 1.02)
        shadow = Shadow(screen, player.img, player.rect.x, player.rect.y, (0, 0, 0), 0)
        shadow.update()
        if radius > WIDTH * 2:
            return
        pygame.display.flip()



def start_screen():
    bg = Background()
    start_game_btn = Button(200, 50, 850, 500, 'start', MenuSM.START, 30)
    leave_game_btn = Button(200, 50, 850, 570, 'leave', MenuSM.LEAVE, 30)
    fon = pygame.image.load(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'menu.png'))
    print_text('R o g u e g e', WIDTH // 2, 400, 'white', 50, centered=True)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        if STATE != MenuSM.MENU:
            return
        screen.fill('black')
        bg.update()
        screen.blit(fon, ((WIDTH - fon.get_size()[0]) // 2, (HEIGHT - fon.get_size()[1]) // 2))
        print_text('R o g u e g e', WIDTH // 2, 400, 'white', 50, centered=True)
        start_game_btn.draw()
        leave_game_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)


def final_screen():
    global FLOOR
    screen.fill('black')
    bg = Background(negative=True)
    fon = pygame.image.load(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'menu.png'))
    restart_game_btn = Button(200, 50, 850, 600, 'restart', MenuSM.START, 30)
    leave_game_btn = Button(200, 50, 850, 670, 'leave', MenuSM.LEAVE, 30)
    print_text('you lose(', WIDTH // 2, 400, 'red', 80, centered=True)
    print_text(f'FLOOR: {FLOOR}', WIDTH // 2, 500, 'white', 70, centered=True)
    pygame.mixer.music.load(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'menu_or_final.mp3'))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        if STATE != MenuSM.FINAL:
            return
        screen.fill('black')
        bg.update()
        screen.blit(fon, ((WIDTH - fon.get_size()[0]) // 2, (HEIGHT - fon.get_size()[1]) // 2))
        print_text('you lose(', WIDTH // 2, 400, 'red', 80, centered=True)
        print_text(f'FLOOR: {FLOOR}', WIDTH // 2, 500, 'white', 70, centered=True)
        restart_game_btn.draw()
        leave_game_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)


def level(player, all_spirtes):
    global STATE
    all_sprites = all_spirtes
    font = pygame.font.Font(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'cool_font.ttf'), 30)
    enemies = pygame.sprite.Group()
    lvl = random.randint(1, 10)
    level = Level(screen, f'level{lvl}.txt')
    player.rect.left = WIDTH // 2
    player.rect.top = HEIGHT // 2
    player.walk_hitbox = pygame.Rect((player.rect.x, player.rect.y + player.rect.height * 0.7, player.rect.width,
                                        player.rect.height * 0.3))
    player.load_obs(level.read_file()[1])
    player.particles.empty()
    with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'enemies', f'enemies{lvl}.txt'), 'r') as f:
        for i in f.readlines():
            pos = [int(x) for x in i.split()]
            bleb = Bleb(screen, 'bleb.png', pos[0], pos[1], all_sprites, player)
            bleb.load_obs(level.read_file()[1])
            enemies.add(bleb)
    player.get_inter_objs(enemies)
    heart = Heart(player, 20, 7)
    bg = Background()
    pygame.mixer.music.load(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'game_music.mp3'))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
        screen.fill('black')
        bg.update()
        level.draw_border(level.read_file()[0])
        print_text(f'FLOOR {FLOOR}', WIDTH // 2, HEIGHT // 2, 'white', 50, centered=True)
        all_sprites.update()
        heart.draw_hp_line(screen)

        if not enemies:
            break

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
        pygame.display.flip()
        clock.tick(FPS)
    transition('white')


def cards(player):
    bg = Background(negative=True)
    cards = pygame.sprite.Group()
    card1 = Card(screen, 'card.png', 100, 1080, cards, player, 0)
    card2 = Card(screen, 'card.png', 735, 1080, cards, player, 200)
    card3 = Card(screen, 'card.png', 1370, 1080, cards, player, 400)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
        screen.fill('white')
        print_text('PICK A CARD', WIDTH // 2, HEIGHT // 2, 'black', 50, centered=True)
        bg.update()
        cards.draw(screen)
        cards.update()
        for card in cards.sprites():
            if any(cards.sprites()) and card.rect.y + card.rect.height < 0:
                return
        pygame.display.flip()


def game():
    global FLOOR
    all_sprites = pygame.sprite.Group()
    player = Player(screen, 'chr.png', WIDTH // 2, HEIGHT // 2, all_sprites)
    FLOOR = 1
    while True:
        transition('black')
        level(player, all_sprites)
        if STATE == MenuSM.FINAL:
            death_animation(player)
            transition('black')
        if STATE != MenuSM.START:
            return
        cards(player)

        FLOOR += 1


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
