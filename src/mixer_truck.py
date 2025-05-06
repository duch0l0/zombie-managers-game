import pygame
from settings import *

TARGET_OFFSET = 30  # Отступ от центра фундамента

class MixerTruck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Инициализация графики
        self.image = pygame.Surface((50, 30))
        self.image.fill((255, 165, 0))  # Ярко-оранжевый цвет
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//4, SCREEN_HEIGHT//4))
        
        # Инициализация всех атрибутов
        self.speed = 3
        self.target_pos = None
        self.pouring = False
        self.pour_time = 0
        self.foundation = None

    def set_target(self, foundation):
        """Устанавливаем цель - фундамент"""
        self.foundation = foundation
        self.target_pos = foundation.rect.center

    def update(self):
        if self.pouring:
            self.pour_time += 1
            if self.pour_time >= 180:  # 3 секунды при FPS=60
                self.complete_pouring()
        elif self.target_pos:
            self.move_to_target()

    def move_to_target(self):
        target_x = self.foundation.rect.centerx + TARGET_OFFSET
        target_y = self.foundation.rect.centery + TARGET_OFFSET
        distance = get_distance(self.rect.centerx, self.rect.centery, target_x, target_y)
        
        if distance > 5:
            # Плавное замедление при приближении
            speed = min(self.speed, distance * 0.3)
            self.rect.x += int((target_x - self.rect.centerx) / distance * speed)
            self.rect.y += int((target_y - self.rect.centery) / distance * speed)


    def start_pouring(self):
        """Начать заливку бетона"""
        self.pouring = True
        self.pour_time = 0
        print("Миксер начал заливку бетона!")

    def complete_pouring(self):
        """Завершить заливку"""
        self.pouring = False
        self.pour_time = 0
        if self.foundation:
            self.foundation.concrete_amount = min(100, self.foundation.concrete_amount + 25)
            print(f"Бетон залит! Текущий уровень: {self.foundation.concrete_amount}%")