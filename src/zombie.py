import pygame
import random
from settings import *

class ZombieManager(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Графика
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Механика движения
        self.speed = ZOMBIE_SPEED
        self.health = 100
        
        # Система сообщений
        self.messages = ["Нужен отчёт!", "Где KPI?", "Cold call!", "Маркетинг!", "Дедлайн!", "Срочно!", "Ревью!", "Бюджет!"]
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