import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Множитель масштаба
        self.scale = 2.5
        
        # Загрузка анимаций для всех направлений
        self.animations = {
            'down': [],
            'up': [],
            'left': [],
            'right': []
        }
        self.load_animations()
        
        # Настройки анимации
        self.current_frame = 0
        self.animation_speed = 0.15
        self.image = self.animations['down'][0]  # Начальный кадр - первая анимация вниз
        self.rect = self.image.get_rect(center=(x, y))
        
        # Характеристики игрока
        self.speed = PLAYER_SPEED
        self.bullet_damage = 10
        self.bullets = pygame.sprite.Group()
        self.direction = 'down'
        self.moving = False

    def load_animations(self):
        """Загружает и масштабирует анимации для всех направлений"""
        base_path = os.path.join(ASSETS_DIR, 'sprites', 'player')
        directions = ['down', 'up', 'left', 'right']
        
        for direction in directions:
            for i in range(1, 9):  # Предполагаем по 8 кадров для каждого направления
                img_path = os.path.join(base_path, direction, f'{i}.png')
                try:
                    image = pygame.image.load(img_path).convert_alpha()
                    # Масштабирование
                    orig_size = image.get_size()
                    scaled_size = (orig_size[0] * self.scale, orig_size[1] * self.scale)
                    image = pygame.transform.scale(image, scaled_size)
                    self.animations[direction].append(image)
                except:
                    print(f"Ошибка загрузки: {img_path}")
                    # Запасной вариант - цветной квадрат
                    fallback = pygame.Surface((32 * self.scale, 32 * self.scale), pygame.SRCALPHA)
                    color = {
                        'down': (0, 255, 0),    # Зеленый - вниз
                        'up': (255, 0, 0),      # Красный - вверх
                        'left': (0, 0, 255),    # Синий - влево
                        'right': (255, 255, 0)  # Желтый - вправо
                    }[direction]
                    pygame.draw.rect(fallback, color, (0, 0, 32 * self.scale, 32 * self.scale))
                    self.animations[direction].append(fallback)

    def animate(self):
        """Обновляет кадр анимации для текущего направления"""
        animation = self.animations[self.direction]
        
        if self.moving:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(animation):
                self.current_frame = 0
        
        self.image = animation[int(self.current_frame)]

    def update(self):
        keys = pygame.key.get_pressed()
        move_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        move_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed
        
        # Определяем направление движения
        if move_y > 0:    # Вниз
            self.direction = 'down'
            self.moving = True
        elif move_y < 0:  # Вверх
            self.direction = 'up'
            self.moving = True
        elif move_x < 0:  # Влево
            self.direction = 'left'
            self.moving = True
        elif move_x > 0:  # Вправо
            self.direction = 'right'
            self.moving = True
        else:
            self.moving = False

        # Нормализация диагонального движения
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        self.rect.x += move_x
        self.rect.y += move_y
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.animate()

    def shoot(self, target_x, target_y):
        bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y, self.bullet_damage)
        self.bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage):
        super().__init__()
        self.damage = damage
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        
        color = (255, 255, 0) if damage <= 15 else (255, 100, 0)
        pygame.draw.circle(self.image, color, (6, 6), 6)
        
        if damage > 15:
            glow = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 150, 0, 100), (8, 8), 8)
            self.image.blit(glow, (-2, -2))

        self.rect = self.image.get_rect(center=(x, y))
        dx = target_x - x
        dy = target_y - y
        dist = max(1, (dx**2 + dy**2)**0.5)
        self.velocity = [dx/dist * 12, dy/dist * 12]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT):
            self.kill()