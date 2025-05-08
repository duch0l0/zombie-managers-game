import pygame
import random
import os
from settings import *

class ZombieManager(pygame.sprite.Sprite):
    def __init__(self, x, y, zombie_type="manager"):
        super().__init__()
        self.scale = 1.0
        self.type = zombie_type
        self.config = ZOMBIE_TYPES[zombie_type]
        
        # Загрузка анимаций
        self.animations = {
            'down': [], 'up': [], 'left': [], 'right': []
        }
        self.load_animations()
        
        # Настройки анимации
        self.current_frame = 0
        self.animation_speed = 0.1
        self.direction = 'down'
        self.image = self.animations[self.direction][0]
        
        # Хитбокс и rect
        self.rect = self.image.get_rect(center=(x, y))
        hitbox_scale = {
            'manager': 0.7,
            'marketing': 0.8,
            'hr': 0.6
        }[self.type]
        self.hitbox = self.rect.inflate(
            -self.rect.width*(1-hitbox_scale),
            -self.rect.height*(1-hitbox_scale)
        )
        
        # Характеристики
        level_mod = LEVELS[current_level]
        self.health = self.config["health"] * (1 + 0.1 * (current_level-1))
        self.speed = self.config["speed"] * level_mod["speed_multiplier"]
        self.hit_distance = 45  # Дистанция атаки фундамента
        
        # Система сообщений
        self.messages = self.config["messages"]
        self.current_message = random.choice(self.messages)
        self.message_alpha = 0
        self.message_timer = 0
        self.message_cooldown = 0

    def load_animations(self):
        """Загружает анимации для текущего типа зомби"""
        base_path = os.path.join(ASSETS_DIR, 'sprites', 'zombies', self.type)
        directions = ['down', 'up', 'left', 'right']
        
        for direction in directions:
            for i in range(1, 11):  # 10 кадров анимации
                img_path = os.path.join(base_path, direction, f'{i}.png')
                try:
                    image = pygame.image.load(img_path).convert_alpha()
                    orig_size = image.get_size()
                    scaled_size = (int(orig_size[0] * self.scale), int(orig_size[1] * self.scale))
                    image = pygame.transform.scale(image, scaled_size)
                    self.animations[direction].append(image)
                except:
                    print(f"Ошибка загрузки: {img_path}")
                    fallback = pygame.Surface((int(30 * self.scale), int(30 * self.scale)), pygame.SRCALPHA)
                    pygame.draw.rect(fallback, self.config["color"], (0, 0, int(30 * self.scale), int(30 * self.scale)))
                    self.animations[direction].append(fallback)

    def animate(self):
        animation = self.animations[self.direction]
        self.current_frame += self.animation_speed
        if self.current_frame >= len(animation):
            self.current_frame = 0
        self.image = animation[int(self.current_frame)]

    def update(self):
        # Движение к центру
        dx = SCREEN_WIDTH//2 - self.rect.centerx
        dy = SCREEN_HEIGHT//2 - self.rect.centery
        distance = max(1, (dx**2 + dy**2)**0.5)
        
        if distance > self.hit_distance:
            # Определение направления
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'

            # Плавное замедление при приближении
            current_speed = self.speed * min(1.0, distance/100)
            
            self.rect.x += dx/distance * current_speed
            self.rect.y += dy/distance * current_speed
            self.hitbox.center = self.rect.center
        else:
            # Атака фундамента
            self.foundation.health -= 10
            self.kill()
            return
        
        self.animate()
        self._update_messages()

    def _update_messages(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            self.message_alpha = min(255, self.message_alpha + 15)
        else:
            self.message_alpha = max(0, self.message_alpha - 5)

        if self.message_cooldown <= 0 and random.random() < 0.005:
            self.current_message = random.choice(self.messages)
            self.message_timer = 90
            self.message_cooldown = 30
        else:
            self.message_cooldown -= 1

    def draw_message(self, surface):
        if self.message_alpha > 0:
            font = pygame.font.Font(None, 24)
            text = font.render(self.current_message, True, (255, 215, 0))
            text.set_alpha(self.message_alpha)
            
            # Позиционирование текста
            text_y_offset = -15 - self.rect.height//4
            text_pos = (
                self.rect.centerx - text.get_width()//2 + random.randint(-2, 2),
                self.rect.y + text_y_offset + random.randint(-1, 1)
            )
            
            # Тень
            shadow = font.render(self.current_message, True, (0, 0, 0))
            shadow.set_alpha(self.message_alpha // 2)
            surface.blit(shadow, (text_pos[0] + 2, text_pos[1] + 2))
            
            surface.blit(text, text_pos)