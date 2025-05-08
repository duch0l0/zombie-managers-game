import pygame
import math
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GREEN, (0, 0, 32, 32), border_radius=5)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEED
        self.bullet_damage = 10  # Базовый урон
        self.bullets = pygame.sprite.Group()
        self.game = None  # Добавляем ссылку на игру

    def update(self):
        keys = pygame.key.get_pressed()
        move_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        move_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        self.rect.x += move_x
        self.rect.y += move_y
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def shoot(self, target_x, target_y):
        bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y, self.bullet_damage)
        self.bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage):
        super().__init__()
        self.damage = damage
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        
        # Базовый вид пули
        color = (255, 255, 0) if damage <= 15 else (255, 100, 0)
        pygame.draw.circle(self.image, color, (6, 6), 6)
        
        # Свечение для улучшенных пуль
        if damage > 15:
            glow = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 150, 0, 100), (8, 8), 8)
            self.image.blit(glow, (-2, -2))

        self.rect = self.image.get_rect(center=(x, y))
        dx = target_x - x
        dy = target_y - y
        dist = max(1, (dx**2 + dy**2)**0.5)
        self.velocity = [dx/dist * 12, dy/dist * 12]  # Увеличенная скорость

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()
