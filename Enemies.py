from ObjectEntity import *


class Enemy(Entity):
    def __init__(self, screen, prev_img, x, y, all_sprites, target, obstacle_level=[]):
        super().__init__(screen, prev_img, x, y, all_sprites, obstacle_level)
        self.MAX_SPEED = 8
        self.ACCELERATION = 2
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.hp = self.MAX_HP
        self.target = target

    def update(self):
        self.position_before_colliding = self.rect
        super().update()
        if self.hp <= 0:
            self.kill()

    def calculate_target_vector(self):
        vector = pygame.math.Vector2(self.target.rect.x - self.rect.x, self.target.rect.y - self.rect.y)
        if vector.length() != 0:
            vector = vector.normalize()
        return vector

    def frict(self):
        if self.direction.length() != 0:
            if round(self.direction.length() * self.FRICTION, 2) != 0:
                self.direction.scale_to_length(self.direction.length() * self.FRICTION)
            else:
                self.direction = pygame.math.Vector2()


class Bleb(Enemy):
    def __init__(self, screen, prev_img, x, y, all_sprites, target, obstacle_level=[]):
        # загрузка анимаций
        self.anim_sheet = self.load_animation('bleb', 5)
        # инит
        super().__init__(screen, prev_img, x, y, all_sprites, target, obstacle_level)
        self.MAX_SPEED = 6
        self.ACCELERATION = 1
        self.FRICTION = 0.9
        self.GRAVITY = 0.9
        self.FALL_GRAVITY = 0.75
        self.BOUNCE_FORCE = 4
        self.MAX_HP = 10
        self.hp = self.MAX_HP

    def update(self):
        self.position_before_colliding = self.rect
        match self.state:
            case StateMachine.IDLE:
                self.change_frame(self.anim_sheet[0 if self.calculate_target_vector().y > 0 else 1], 0.2)
                self.count_frames += 1
                self.direction = self.calculate_target_vector()
            case StateMachine.STUN:
                self.check_stun()
        self.move_towards(self.MAX_SPEED, self.ACCELERATION)
        if self.hp <= 0:
            self.kill()
        super().update()

    def load_animation(self, base, columns):
        sheets = []
        img = self.load_image(f'{base}-down.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        img = self.load_image(f'{base}-up.png')
        sheets.append(self.cut_sheet(img, columns, 1))
        return sheets

    def interact(self):
        if self.target.state == StateMachine.ATTACK and self.state != StateMachine.STUN:
            self.get_damaged(1)
            self.state = StateMachine.STUN
            self.resist_time = pygame.time.get_ticks()
            self.direction = pygame.math.Vector2(self.target.direction.x, self.target.direction.y)
            self.target.stop()
        elif self.target.state != StateMachine.ATTACK and self.target.state != StateMachine.STUN \
                and self.state != StateMachine.STUN:
            self.target.get_damaged(1)
            print(self.target.state)
            self.target.state = StateMachine.STUN
            self.target.direction = pygame.math.Vector2(self.direction.x, self.direction.y)
            self.velocity = pygame.math.Vector2()
