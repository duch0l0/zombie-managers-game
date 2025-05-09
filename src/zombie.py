import pygame
import random
import os
from settings import *

class ZombieManager(pygame.sprite.Sprite):
    def __init__(self, x, y, zombie_type="manager"):
        super().__init__()
        self.scale = 2
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
            'manager': 0.5,
            'marketing': 0.5,
            'hr': 0.5
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

    def animate(self):  # <- Новый метод
        animation = self.animations[self.direction]
        self.current_frame += self.animation_speed
        if self.current_frame >= len(animation):
            self.current_frame = 0
        self.image = animation[int(self.current_frame)]

    def load_animations(self):
        """Загружает анимации для всех направлений"""
        base_path = os.path.join(ASSETS_DIR, 'sprites', 'zombies', self.type)
        directions = ['down', 'up', 'left', 'right']  # Добавьте эту строку
        
        for direction in directions:
            for i in range(1, 11):  # 10 кадров анимации
                img_path = os.path.join(base_path, direction, f'{i}.png')
                try:
                    image = pygame.image.load(img_path).convert_alpha()
                    self.animations[direction].append(image)
                except Exception as e:
                    print(f"Ошибка загрузки: {img_path} - {e}")
                    # Создаем запасной спрайт
                    fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
                    pygame.draw.rect(fallback, self.config["color"], (0, 0, 32, 32))
                    self.animations[direction].append(fallback)

    def update(self):
        # 1. Проверяем наличие фундамента
        if not hasattr(self, 'foundation') or not self.foundation:
            return

        # 2. Движение к центру фундамента (не экрана!)
        target_x, target_y = self.foundation.rect.center
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = max(1, (dx**2 + dy**2)**0.5)
        
        # 3. Отладочный вывод (можно убрать после фикса)
        print(f"{self.type} Zombie: distance={distance:.1f}, hit_distance={self.hit_distance}")
        
        if distance > self.hit_distance:
            # Определение направления
            if abs(dx) > abs(dy):
                self.direction = 'right' if dx > 0 else 'left'
            else:
                self.direction = 'down' if dy > 0 else 'up'

            # Движение без плавного замедления (для точного попадания)
            self.rect.x += dx/distance * self.speed
            self.rect.y += dy/distance * self.speed
            self.hitbox.center = self.rect.center
        else:
            # Атака фундамента
            print(f"{self.type} Zombie attacking foundation!")  # Логирование
            self.foundation.health -= 10
            self.kill()
            return
        
        # 4. Обновляем анимацию и сообщения (один раз за кадр)
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
            
            # Фиксированный отступ от центра зомби
            text_y_offset = -25  # Настраиваемое значение
            text_pos = (
                self.rect.centerx - text.get_width()//2 + random.randint(-2, 2),
                self.rect.centery + text_y_offset + random.randint(-1, 1)  # Используем centery вместо y
            )
            
            # Тень (оставляем без изменений)
            shadow = font.render(self.current_message, True, (0, 0, 0))
            shadow.set_alpha(self.message_alpha // 2)
            surface.blit(shadow, (text_pos[0] + 2, text_pos[1] + 2))
            
            surface.blit(text, text_pos)