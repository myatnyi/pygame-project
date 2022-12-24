import pygame
import sys
import math

FPS = 50
pygame.init()
pygame.display.set_caption('Жока и бока')
size = WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
MAX_SPEED = 50
ACCELERATION = 5
FRICTION = 0.9

DEBUG = True

def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["типа меню", "",
                  "типа кнопка",
                  "да",
                  "нет"]

    screen.fill('blue')
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def game():
    font = pygame.font.Font(None, 30)
    pos = [WIDTH // 2, HEIGHT // 2]
    velocity = pygame.math.Vector2(0, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                terminate()
        key = pygame.key.get_pressed()
        up = key[pygame.K_w] or key[pygame.K_UP]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]
        direction = pygame.math.Vector2(right - left, down - up)
        if direction.length() != 0:
            direction = direction.normalize()
            velocity += ACCELERATION * direction
            if velocity.length() >= MAX_SPEED:
                velocity.scale_to_length(MAX_SPEED)
        else:
            velocity[0] *= FRICTION
            velocity[0] = math.trunc(velocity[0])
            velocity[1] *= FRICTION
            velocity[1] = math.trunc(velocity[1])

        pos[0] += velocity[0]
        pos[1] += velocity[1]
        screen.fill('black')
        
        if DEBUG:
            string_rendered = font.render(str(velocity), True, 'white')
            intro_rect = string_rendered.get_rect()
            intro_rect.top = pos[1] + 20
            intro_rect.x = pos[0] - intro_rect.width // 2
            screen.blit(string_rendered, intro_rect)
        
        pygame.draw.circle(screen, 'red', pos, 25)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    start_screen()
    game()

