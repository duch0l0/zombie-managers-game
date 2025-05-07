import pygame
import random
from settings import *

class UpgradeEffects:
    @staticmethod
    def bullet_effect(bullet):
        """Визуальный эффект для улучшенных пуль"""
        if bullet.damage > 15:  # Если улучшен урон
            bullet.image.fill((255, 100, 0))  # Оранжевый
            glow = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 150, 0, 100), (6, 6), 6)
            bullet.image = glow

    @staticmethod
    def mixer_effect(mixer):
        """Эффект для быстрых миксеров"""
        if mixer.speed > 3.0:
            # Создаем эффект "движущихся полос"
            mixer.image.fill((255, 165, 0))  # Базовый цвет
            for i in range(3):
                offset = (pygame.time.get_ticks() // 100) % 20 - 10
                pygame.draw.rect(
                    mixer.image, 
                    (255, 200, 100),
                    (0, 5 + i*10 + offset, 50, 3))
    
    @staticmethod
    def foundation_effect(foundation):
        """Эффект для укрепленного фундамента"""
        if foundation.max_health > 1000:
            # Пульсирующая рамка
            alpha = 100 + int(100 * abs(pygame.math.Vector2(0, 1).rotate(pygame.time.get_ticks() / 10).y))
            overlay = pygame.Surface((110, 110), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 200, 255, alpha), (0, 0, 110, 110), 3)
            foundation.image.blit(overlay, (-5, -5))