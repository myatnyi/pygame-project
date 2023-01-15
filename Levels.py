import pygame
import pathlib
import os


class Level:
    def __init__(self, screen, filename):
        self.filename = filename
        self.screen = screen

    def read_file(self):
        lines = []
        with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'levels', self.filename), 'r') as file:
            list_coords = []
            with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'levels', self.filename), 'r') as file:
                for line in file.readlines():
                    coords = [int(num) for num in line.split()]
                    list_coords.append(coords)
                for i in range(len(list_coords)):
                    if list_coords[i] == list_coords[-1]:
                        lines.append(pygame.draw.line(self.screen, 'white', list_coords[i], list_coords[0], 10))
                    else:
                        lines.append(pygame.draw.line(self.screen, 'white', list_coords[i], list_coords[i + 1], 10))

            return list_coords, lines

    def draw_border(self, coords):
        border = pygame.draw.lines(self.screen, 'white', True, coords, 10)
        pygame.draw.polygon(self.screen, 'black', coords)
