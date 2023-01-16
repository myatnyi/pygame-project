import pygame
import os
import pathlib
import sys

FPS = 60
pygame.init()
pygame.display.set_caption('generator')
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, group):
        super().__init__(group)
        names = [os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'export-off.png'),
                 os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'export-on.png')]
        self.images = []
        for name in names:
            self.images.append(pygame.image.load(name))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def update(self, statement, points):
        pos = pygame.mouse.get_pos()
        mouse = pygame.mouse.get_pressed()
        if self.rect.collidepoint(pos) and statement:
            self.image = self.images[1]
            if mouse[0]:
                path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'levels')
                if os.listdir(path):
                    name = f"level{int(sorted(os.listdir(path))[-1].lstrip('level').rstrip('.txt')) + 1}.txt"
                else:
                    name = 'level1.txt'
                with open(os.path.join(path, name), 'w') as f:
                    for point in points:
                        f.write(f'{point[0][0]} {point[0][1]}\n')
                print('Succed')
                pygame.quit()
                sys.exit()
        else:
            self.image = self.images[0]


def sc():
    grid = pygame.Surface((WIDTH, HEIGHT))
    offset = 40
    pos0 = None
    pos1 = None
    start_painting = False
    end_painting = False
    points = []
    button_group = pygame.sprite.Group()
    button = Button(WIDTH - 80, HEIGHT - 30, button_group)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not start_painting:
                pos0 = list(event.pos)
                start_painting = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not end_painting:
                points.append([pos0, pos1])
                pos0 = pos1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and pygame.key.get_mods() and pygame.KMOD_CTRL:
                    if points:
                        pos0 = points[-2][1] if len(points) > 1 else points[0][0]
                        points.pop()
        screen.fill('black')
        for i in range(offset, WIDTH - offset + 1, offset):
            pygame.draw.line(grid, 'white', (i, offset), (i, HEIGHT - offset), 2)
        for i in range(offset, HEIGHT - offset + 1, offset):
            pygame.draw.line(grid, 'white', (offset, i), (WIDTH - offset, i), 2)
        pygame.draw.line(grid, 'blue', (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
        pygame.draw.line(grid, 'red', (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)
        grid.set_alpha(100)
        screen.blit(grid, (0, 0))
        pos1 = list(pygame.mouse.get_pos())
        for point in points:
            pygame.draw.line(screen, 'white', point[0], point[1], 3)
        if points and points[0][0] == points[-1][1]:
            end_painting = True
        if start_painting and not end_painting:
            if pos0[0] < offset:
                pos0[0] = offset
            elif pos0[0] > WIDTH - offset:
                pos0[0] = WIDTH - offset
            if pos0[1] < offset:
                pos0[1] = offset
            elif pos0[1] > HEIGHT - offset:
                pos0[1] = HEIGHT - offset
            if pos1[0] < offset:
                pos1[0] = offset
            elif pos1[0] > WIDTH - offset:
                pos1[0] = WIDTH - offset
            if pos1[1] < offset:
                pos1[1] = offset
            elif pos1[1] > HEIGHT - offset:
                pos1[1] = HEIGHT - offset
            pos0 = [round(pos0[0] / offset) * offset, round(pos0[1] / offset) * offset]
            pos1 = [round(pos1[0] / offset) * offset, pos0[1]] if abs(pos1[0] - pos0[0]) > abs(pos1[1] - pos0[1]) else [pos0[0], round(pos1[1] / offset) * offset]
            pygame.draw.line(screen, 'white', pos0, pos1, 3)
            font = pygame.font.Font(None, 30)
            text = font.render(str(pos1), True, pygame.Color('white'))
            screen.blit(text, (0, 0))
        button.update(end_painting, points)
        button_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    sc()

