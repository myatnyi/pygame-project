from ObjectEntity import *


class Player(Entity):
    def __init__(self, screen, prev_img, x, y, all_sprites, obstacle_level=[]):
        # загрузка анимаций
        self.idle_sheet = self.load_animation('chr-idle', 5)
        self.walk_sheet = self.load_animation('chr-walk', 5)
        self.attack_sheet = self.load_animation('chr-attack', 5)
        self.shield_sheet = self.load_animation('chr-shield', 1)
        self.roll_sheet = self.load_animation('chr-roll', 1)
        dead_img = self.load_image(f'chr-dead')
        self.dead_sheet = self.cut_sheet(dead_img, 1, 1)
        # инит
        super().__init__(screen, prev_img, x, y, all_sprites, obstacle_level)
        self.state = StateMachine.IDLE
        self.MAX_SPEED = 8
        self.ACCELERATION = 2
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.hp = self.MAX_HP
        self.inter_objs = []

    def update(self):
        previous_state = self.state
        self.position_before_colliding = self.rect
        match self.state:
            case StateMachine.IDLE:
                self.walk_towards()
                self.attack()
                self.shield()
                self.roll()
                self.idle_animation()
            case StateMachine.WALK:
                self.walk_towards()
                self.attack()
                self.shield()
                self.roll()
                self.walk_animation()
            case StateMachine.ROLL:
                self.roll_animation()
            case StateMachine.ATTACK:
                self.attack_animation()
            case StateMachine.SHIELD:
                self.shield_animation()
            case StateMachine.STUN:
                self.check_stun()
                self.move_towards(200, 20)
        if previous_state != self.state:
            self.cur_frame = 0
        if self.hp <= 0:
            self.death_animation()
        self.count_frames += 1
        super().update()
        self.info = self.state

# функции состояний
    def walk_towards(self):
        self.state = StateMachine.WALK
        self.calculate_direction()
        self.move_towards(self.MAX_SPEED, self.ACCELERATION)
        self.bounce_towards()

    def attack(self):
        button = pygame.mouse.get_pressed()
        if button[0]:
            self.direction = self.mouse_vector()
            self.state = StateMachine.ATTACK

    def shield(self):
        button = pygame.mouse.get_pressed()
        if button[2]:
            self.state = StateMachine.SHIELD

    def roll(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.state = StateMachine.ROLL

    def calculate_direction(self):
        key = pygame.key.get_pressed()
        up = key[pygame.K_w] or key[pygame.K_UP]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]
        self.direction = pygame.Vector2(right - left, down - up)
        if self.direction.length() == 0:
            self.state = StateMachine.IDLE

    def mouse_vector(self):
        mouse_pos = pygame.mouse.get_pos()
        pos = (mouse_pos[0] - self.rect.x - self.rect.width // 2, mouse_pos[1] - self.rect.y - self.rect.height // 2)
        vector = pygame.math.Vector2(pos)
        if vector.length() != 0:
            vector = vector.normalize()
        return vector

    def mouse_degree(self):
        vector = self.mouse_vector()
        return math.atan2(vector.y, vector.x) * 180 / math.pi + (360 if vector.y < 0 else 0)

    def draw_shadow(self):
        self.particles.add(Shadow(self.screen, self.image, self.rect.x, self.rect.y))

# анимации к состояниям
    def determine_sheet(self):
        ranges = [range(0, 60), range(60, 120), range(120, 180), range(180, 240), range(240, 300), range(30, 360)]
        for i in range(len(ranges)):
            if int(self.mouse_degree()) in ranges[i]:
                return i

    def idle_animation(self):
        self.change_frame(self.idle_sheet[self.determine_sheet()], 0.1)

    def walk_animation(self):
        self.change_frame(self.walk_sheet[self.determine_sheet()], 0.2)
        self.bounce_rotate(10, 100)
        if self.cur_frame == 2:
            self.bounce_vel += self.BOUNCE_FORCE

    def attack_animation(self):
        self.draw_shadow()
        self.change_frame(self.attack_sheet[self.determine_sheet()], 0.1 if 2 <= self.cur_frame < 4 else 0.5)
        if self.cur_frame < 3:
            self.move_towards(8, 4)
        else:
            self.move_towards(2, 1)
        if self.cur_frame == 4:
            self.state = StateMachine.IDLE

    def roll_animation(self):
        # код
        self.state = StateMachine.IDLE
        self.cur_frame = 0

    def shield_animation(self):
        # код
        self.state = StateMachine.IDLE
        self.cur_frame = 0

    def death_animation(self):
        self.kill()

    def collision_interact(self):
        for group in self.inter_objs:
            for inter in pygame.sprite.spritecollide(self, group, False, pygame.sprite.collide_mask):
                inter.interact()

    def get_inter_objs(self, *inter_objs):
        self.inter_objs = inter_objs