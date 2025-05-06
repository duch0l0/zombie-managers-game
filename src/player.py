import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEED  # Из settings.py
        self.last_update = pygame.time.get_ticks()
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0

    def update(self):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        # Обнуляем скорость перед вычислением
        move_x, move_y = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y = self.speed

        # Диагональное движение (нормализация)
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071  # 1/sqrt(2)
            move_y *= 0.7071

        # Применяем движение
        self.rect.x += move_x
        self.rect.y += move_y

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Ограничение границами экрана
        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - self.rect.height, self.rect.y))
    
    def shoot(self, target_x, target_y):
        if not hasattr(self, 'bullets'):
            self.bullets = pygame.sprite.Group()  # Создаем группу при первом вызове
        
        bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y)
        self.bullets.add(bullet)  # Правильное добавление в группу


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        pygame.sprite.Sprite.__init__(self)  # Важно: вызываем родительский конструктор
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))  # Желтый цвет
        self.rect = self.image.get_rect(center=(x, y))
        
        # Расчет направления
        dx = target_x - x
        dy = target_y - y
        distance = max(1, (dx**2 + dy**2)**0.5)
        self.vx = dx / distance * 10
        self.vy = dy / distance * 10

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        # Удаление за границами экрана
        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()
        