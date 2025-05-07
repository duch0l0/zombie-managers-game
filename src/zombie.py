import pygame
import random
from settings import *
from settings import LEVELS, current_level  # Добавляем эту строку

class ZombieManager(pygame.sprite.Sprite):
    def __init__(self, x, y, zombie_type="manager"):
        super().__init__()
        
        from settings import current_level, LEVELS  # Импортируем здесь
        
        config = ZOMBIE_TYPES[zombie_type]
        level_mod = LEVELS[current_level]
        
        self.speed = config["speed"] * level_mod["speed_multiplier"]
        self.health = config["health"] * (1 + 0.1 * (current_level-1))
        self.type = zombie_type
        config = ZOMBIE_TYPES[zombie_type]
        
        self.image = pygame.Surface((30, 30))
        self.image.fill(config["color"])
        self.rect = self.image.get_rect(center=(x, y))
        
        self.health = config["health"]
        self.speed = config["speed"] * LEVELS[current_level]["speed_multiplier"]
        
        # Система сообщений
        self.messages = ["Дай скидку!", "Где KPI?", "Ишак тебя понюхал!", "Никита не ходит на встречи!", "Дедлайн!", "АБН не встанет!", "Ревью!", "Бюджет!"]
        self.current_message = random.choice(self.messages)
        self.message_alpha = 0    # Прозрачность (0-255)
        self.message_timer = 0    # Таймер показа
        self.message_cooldown = 0 # Задержка между сообщениями

    def update(self):
        # Движение к центру (фундаменту)
        distance = get_distance(self.rect.centerx, self.rect.centery,
                              SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        if distance > 5:
            dx = (SCREEN_WIDTH//2 - self.rect.centerx) / distance
            dy = (SCREEN_HEIGHT//2 - self.rect.centery) / distance
            self.rect.x += int(dx * self.speed)
            self.rect.y += int(dy * self.speed)

        # Обновление системы сообщений
        self._update_messages()

    def _update_messages(self):
        """Обновление состояния сообщений"""
        # Таймер прозрачности
        if self.message_timer > 0:
            self.message_timer -= 1
            self.message_alpha = min(255, self.message_alpha + 15)  # Появление
        else:
            self.message_alpha = max(0, self.message_alpha - 5)     # Исчезание

        # Случайная смена сообщения
        if self.message_cooldown <= 0 and random.random() < 0.005:  # 0.5% шанс
            self.current_message = random.choice(self.messages)
            self.message_timer = 90  # Показывать 1.5 секунды (при FPS=60)
            self.message_cooldown = 30
        else:
            self.message_cooldown -= 1

    def draw_message(self, surface):
        """Отрисовка сообщения над зомби"""
        if self.message_alpha > 0:
            font = pygame.font.Font(None, 24)
            
            # Рендер текста с обводкой (как в Fallout)
            text = font.render(self.current_message, True, (255, 215, 0))  # Золотой
            text.set_alpha(self.message_alpha)
            
            # Позиция над головой зомби + случайное дрожание
            offset_x = random.randint(-2, 2)  # Эффект "дрожания"
            text_pos = (self.rect.centerx - text.get_width()//2 + offset_x, 
                       self.rect.y - 25 + random.randint(-1, 1))
            
            # Тень для лучшей читаемости
            shadow = font.render(self.current_message, True, (0, 0, 0))
            shadow.set_alpha(self.message_alpha // 2)
            surface.blit(shadow, (text_pos[0] + 2, text_pos[1] + 2))
            
            surface.blit(text, text_pos)