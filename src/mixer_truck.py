import pygame
import random
from settings import *

class MixerTruck(pygame.sprite.Sprite):
    base_speed = 2.5  # Базовая скорость миксера

    def __init__(self):
        super().__init__()
        self.animations = self._load_animations()
        self.image = self.animations['right'][0]  # Начальный кадр анимации
        self.rect = self.image.get_rect()
        self.speed = self.__class__.base_speed
        self.foundation = None
        self.pouring = False
        self.pour_time = 0
        self._spawn_off_screen()
        self.leaving = False
        self.leave_speed = 3
        self.current_frame = 0
        self.animation_speed = 0.1
        self.direction = 'right'  # Начальное направление

    def _spawn_off_screen(self):
        """Спавн миксера за пределами экрана (только с левой/правой стороны)"""
        side = random.choice(['left', 'right'])
        if side == 'right':
            self.rect.midleft = (SCREEN_WIDTH + 10, random.randint(0, SCREEN_HEIGHT))
            self.direction = 'left'  # При появлении справа - кабина слева
        else:
            self.rect.midright = (-10, random.randint(0, SCREEN_HEIGHT))
            self.direction = 'right'  # При появлении слева - кабина справа

    def set_target(self, foundation):
        """Установка цели для миксера"""
        self.foundation = foundation

    def update(self):
        """Основной метод обновления состояния миксера"""
        if self.leaving:
            self._handle_leaving()
        elif self.pouring:
            self._handle_pouring()
        else:
            self._move_to_target()
        
        # Обновление анимации
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.animations[self.direction]):
            self.current_frame = 0
        self.image = self.animations[self.direction][int(self.current_frame)]

    def _move_to_target(self):
        """Движение к цели (опалубке)"""
        if not self.foundation:
            return
            
        target = self.foundation.rect.center
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        dist = (dx**2 + dy**2)**0.5
        
        # Определение направления движения
        if dx < 0:  # Движение влево
            self.direction = 'right'  # Кабина справа
        else:        # Движение вправо
            self.direction = 'left'   # Кабина слева
        
        if dist > TARGET_OFFSET:
            self.rect.x += dx/dist * self.speed
            self.rect.y += dy/dist * self.speed
        else:
            self.start_pouring()

    def start_pouring(self):
        """Начало заливки бетона"""
        self.pouring = True
        self.pour_time = 0

    def _handle_pouring(self):
        """Обработка процесса заливки"""
        self.pour_time += 1
        if self.pour_time >= FPS * 3:  # 3 секунды заливки
            self._complete_pouring()

    def _complete_pouring(self):
        """Завершение заливки"""
        if self.foundation:
            self.foundation.concrete_amount = min(100, self.foundation.concrete_amount + 10)
        self._exit_site()

    def _exit_site(self):
        """Подготовка к отъезду"""
        self.leaving = True
        self.leave_direction = random.choice(['left', 'right'])  # Только горизонтальный отъезд
        
        # Установка правильной анимации
        if self.leave_direction == 'left':
            self.direction = 'right'  # Кабина справа при движении влево
        else:
            self.direction = 'left'    # Кабина слева при движении вправо
        
        # Установка целевых координат
        if self.leave_direction == 'left':
            self.target_x = -self.rect.width
        else:
            self.target_x = SCREEN_WIDTH + self.rect.width

    def _handle_leaving(self):
        """Обработка отъезда миксера"""
        if self.leave_direction == 'left':
            self.rect.x -= self.leave_speed
            if self.rect.right <= 0:
                self.kill()
        else:
            self.rect.x += self.leave_speed
            if self.rect.left >= SCREEN_WIDTH:
                self.kill()

    def _load_animations(self):
        animations = {'left': [], 'right': []}
        scale_factor = 1.5
        
        for direction in animations.keys():
            for i in range(1, 5):
                try:
                    img = pygame.image.load(f"assets/sprites/mixer_truck/{direction}/{i}.png").convert_alpha()
                    orig_size = img.get_size()
                    new_size = (int(orig_size[0] * scale_factor), int(orig_size[1] * scale_factor))
                    img = pygame.transform.scale(img, new_size)
                    animations[direction].append(img)
                except:
                    new_width, new_height = int(50 * scale_factor), int(30 * scale_factor)
                    surf = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
                    color = (255, 165, 0) if direction == 'right' else (200, 140, 0)
                    pygame.draw.rect(surf, color, (0, 0, new_width, new_height))
                    animations[direction].append(surf)
        return animations