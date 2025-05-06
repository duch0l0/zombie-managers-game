import pygame
from settings import *

class Foundation(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.health = 1000
        self.max_health = 1000
        self.concrete_amount = 0  # 0-100%
        
    def update(self):
        # Визуализация прогресса заливки
        if self.concrete_amount > 0:
            progress = self.concrete_amount / 100
            pygame.draw.rect(
                self.image, 
                (100, 100, 100),  # Цвет бетона
                (0, 0, 100 * progress, 100)
            )