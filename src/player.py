import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEED
        self.bullet_damage = 10  # Базовый урон
        self.bullets = pygame.sprite.Group()

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
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        
        dx = target_x - x
        dy = target_y - y
        dist = max(1, (dx**2 + dy**2)**0.5)
        self.velocity = [dx/dist * 10, dy/dist * 10]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()
        