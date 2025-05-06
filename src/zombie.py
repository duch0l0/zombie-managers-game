import pygame
import random
from settings import *

class ZombieManager(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)  # Ярко-красный цвет
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ZOMBIE_SPEED
        self.health = 100
        self.messages = ["Нужен отчёт!", "Где KPI?", "Cold call!"]
        self.current_message = random.choice(self.messages)

    def update(self):
        distance = get_distance(self.rect.centerx, self.rect.centery,
                            SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        if distance > 5:
            dx = (SCREEN_WIDTH//2 - self.rect.centerx) / distance
            dy = (SCREEN_HEIGHT//2 - self.rect.centery) / distance
            self.rect.x += int(dx * self.speed)
            self.rect.y += int(dy * self.speed)