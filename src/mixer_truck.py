import pygame
import random
from settings import *

class MixerTruck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill((255, 165, 0))
        self.speed = 2.5  # Оптимальная скорость
        self.pouring = False
        self.pour_time = 0
        self.foundation = None
        self._spawn_off_screen()

    def _spawn_off_screen(self):
        """Спавн в случайной точке за границами экрана"""
        side = random.randint(0, 3)
        if side == 0:  # top
            self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), -50))
        elif side == 1:  # right
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT)))
        elif side == 2:  # bottom
            self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50))
        else:  # left
            self.rect = self.image.get_rect(center=(-50, random.randint(0, SCREEN_HEIGHT)))

    def update(self):
        if self.pouring:
            self._handle_pouring()
        else:
            self._move_to_target()

    def _move_to_target(self):
        """Плавное движение с использованием get_distance()"""
        if not self.foundation:
            return

        target_pos = self.foundation.rect.center
        current_pos = self.rect.center
        distance = get_distance(*current_pos, *target_pos)
        
        if distance > 1:  # Остановка в 1px от цели
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            self.rect.x += int(dx / distance * self.speed)
            self.rect.y += int(dy / distance * self.speed)
        else:
            self.start_pouring()

    def _handle_pouring(self):
        """Обработка процесса заливки"""
        self.pour_time += 1
        if self.pour_time >= FPS * 3:  # Ровно 3 секунды
            self._complete_pouring()

    def start_pouring(self):
        self.pouring = True
        self.pour_time = 0

    def _complete_pouring(self):
        """Завершение заливки и уход с площадки"""
        if self.foundation:
            self.foundation.concrete_amount = min(100, self.foundation.concrete_amount + 10)
        self._exit_site()

    def _exit_site(self):
        """Плавный уход за границы экрана"""
        # Выбираем случайную сторону для ухода
        side = random.choice(['top', 'right', 'bottom', 'left'])
        if side == 'top':
            self.rect.y = -self.rect.height
        elif side == 'right':
            self.rect.x = SCREEN_WIDTH
        elif side == 'bottom':
            self.rect.y = SCREEN_HEIGHT
        else:  # left
            self.rect.x = -self.rect.width
        self.kill()
    
    def set_target(self, foundation):
        """Устанавливает цель (фундамент) для миксерного грузовика"""
        self.foundation = foundation