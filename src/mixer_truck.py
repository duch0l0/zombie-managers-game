import pygame
import random
from settings import *

class MixerTruck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill((255, 165, 0))  # Оранжевый цвет
        self.speed = 1.5
        self.pouring = False
        self.pour_time = 0
        self.foundation = None
        self.exiting = False  # Флаг для состояния ухода
        self.exit_speed = 2.5  # Скорость ухода с площадки
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
        if self.exiting:
            self._handle_exiting()  # Обработка ухода с площадки
        elif self.pouring:
            self._handle_pouring()  # Обработка заливки
        else:
            self._move_to_target()  # Движение к цели

    def _move_to_target(self):
        """Движение к фундаменту с фиксированным радиусом остановки"""
        if not hasattr(self, 'foundation') or not self.foundation:
            return  # Ждем установки цели

        target_pos = self.foundation.rect.center
        current_pos = self.rect.center
        distance = get_distance(*current_pos, *target_pos)
        
        if distance > TARGET_OFFSET:
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            self.rect.x += int(dx / distance * self.speed)
            self.rect.y += int(dy / distance * self.speed)
        else:
            self.start_pouring()

    def _handle_pouring(self):
        """Процесс заливки бетона (3 секунды)"""
        self.pour_time += 1
        if self.pour_time >= FPS * 3:
            self._complete_pouring()

    def start_pouring(self):
        """Начало заливки"""
        self.pouring = True
        self.pour_time = 0

    def _complete_pouring(self):
        """Завершение заливки и начало ухода"""
        if self.foundation:
            self.foundation.concrete_amount = min(100, self.foundation.concrete_amount + 10)
        self._start_exiting()

    def _start_exiting(self):
        """Подготовка к уходу с площадки"""
        self.pouring = False
        self.exiting = True
        # Выбираем случайную сторону для ухода
        self.exit_side = random.choice(['top', 'right', 'bottom', 'left'])
        # Устанавливаем высокую скорость для ухода
        self.speed = self.exit_speed

    def _handle_exiting(self):
        """Процесс ухода с площадки"""
        if self.exit_side == 'top':
            self.rect.y -= self.exit_speed
            if self.rect.bottom < 0:
                self.kill()
        elif self.exit_side == 'right':
            self.rect.x += self.exit_speed
            if self.rect.left > SCREEN_WIDTH:
                self.kill()
        elif self.exit_side == 'bottom':
            self.rect.y += self.exit_speed
            if self.rect.top > SCREEN_HEIGHT:
                self.kill()
        else:  # left
            self.rect.x -= self.exit_speed
            if self.rect.right < 0:
                self.kill()

    def set_target(self, foundation):
        """Установка цели (фундамента)"""
        self.foundation = foundation