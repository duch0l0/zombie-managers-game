import os
import math
import pygame

# Отступ от центра фундамента для остановки миксера
TARGET_OFFSET = 30

CONCRETE_PER_MIXER = 10  # 10% бетона за заливку

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, '../assets')

# Окно
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Персонажи
PLAYER_SPEED = 5
ZOMBIE_SPEED = 2

def get_distance(x1, y1, x2, y2):
    """Безопасный расчет расстояния между точками"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) or 1.0  # Избегаем деления на 0