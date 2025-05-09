import pygame
import random
from settings import *

class MixerTruck(pygame.sprite.Sprite):
    base_speed = 2.5  # Классовая переменная для скорости

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.animations = self._load_animations()
        self.image = self.animations['down'][0]
        self.rect = self.image.get_rect()
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect()
        self.speed = self.__class__.base_speed  # Используем классовую скорость
        self.foundation = None
        self.pouring = False
        self.pour_time = 0
        self._spawn_off_screen()

    def _spawn_off_screen(self):
        side = random.choice(['top', 'right', 'bottom', 'left'])
        if side == 'top':
            self.rect.midbottom = (random.randint(0, SCREEN_WIDTH), -10)
        elif side == 'right':
            self.rect.midleft = (SCREEN_WIDTH + 10, random.randint(0, SCREEN_HEIGHT))
        elif side == 'bottom':
            self.rect.midtop = (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 10)
        else:
            self.rect.midright = (-10, random.randint(0, SCREEN_HEIGHT))

    def set_target(self, foundation):
        self.foundation = foundation

    def update(self):
        if self.pouring:
            self._handle_pouring()
        else:
            self._move_to_target()

    def _move_to_target(self):
        if not self.foundation:
            return
            
        target = self.foundation.rect.center
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        dist = max(1, (dx**2 + dy**2)**0.5)
        
        if dist > TARGET_OFFSET:
            self.rect.x += dx/dist * self.speed
            self.rect.y += dy/dist * self.speed
        else:
            self.start_pouring()

    def start_pouring(self):
        self.pouring = True
        self.pour_time = 0

    def _handle_pouring(self):
        self.pour_time += 1
        if self.pour_time >= FPS * 3:  # 3 секунды заливки
            self._complete_pouring()

    def _complete_pouring(self):
        if self.foundation:
            self.foundation.concrete_amount = min(100, self.foundation.concrete_amount + 10)
        self._exit_site()

    def _exit_site(self):
        side = random.choice(['top', 'right', 'bottom', 'left'])
        if side == 'top':
            self.rect.y = -self.rect.height
        elif side == 'right':
            self.rect.x = SCREEN_WIDTH
        elif side == 'bottom':
            self.rect.y = SCREEN_HEIGHT
        else:
            self.rect.x = -self.rect.width
        self.kill()
    
    def _load_animations(self):
        animations = {'down': [], 'up': [], 'left': [], 'right': []}
        for direction in animations.keys():
            for i in range(1, 5):  # 4 кадра анимации
                try:
                    img = pygame.image.load(
                        f"assets/sprites/mixer_truck/{direction}/{i}.png"
                    ).convert_alpha()
                    animations[direction].append(img)
                except:
                    # Запасной вариант
                    surf = pygame.Surface((50, 30), pygame.SRCALPHA)
                    color = (255, 165, 0) if direction == 'down' else (200, 140, 0)
                    pygame.draw.rect(surf, color, (0, 0, 50, 30))
                    animations[direction].append(surf)
        return animations