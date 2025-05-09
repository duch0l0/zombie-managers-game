import os
import math
import pygame

# Отступ от центра фундамента для остановки миксера
TARGET_OFFSET = 70

CONCRETE_PER_MIXER = 10  # 10% бетона за заливку

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, '../assets')

# Окно
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
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
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)

# Уровни сложности
LEVELS = {
    1: {
        "zombie_spawn_rate": 90,  # Частота спавна (в кадрах)
        "speed_multiplier": 1.0,
        "max_zombies": 10,
        "required_kills": 15  # Сколько зомби нужно убить для перехода
    },
    2: {
        "zombie_spawn_rate": 60,
        "speed_multiplier": 1.3,
        "max_zombies": 15,
        "required_kills": 25
    },
    3: {
        "zombie_spawn_rate": 40,
        "speed_multiplier": 1.7,
        "max_zombies": 20,
        "required_kills": 40
    }
}
current_level = 1  # Текущий уровень

# Типы зомби (цвет, здоровье, скорость, фразы)
ZOMBIE_TYPES = {
    "manager": {
        "hit_distance": 45,
        "base_width": 32,  
        "base_height": 32, 
        "color": RED,
        "health": 100,
        "speed": 2.0,
        "messages": ["Нужен отчёт!", "Где KPI?", "Cold call!"]
    },
    "marketing": {
        "hit_distance": 45,
        "base_width": 32,  
        "base_height": 32, 
        "color": (148, 0, 211),  # Фиолетовый
        "health": 300,
        "speed": 1,
        "messages": ["ВирАльность!", "Охват падает!", "Нужен контент!"]
    },
    "hr": {
        "hit_distance": 45,
        "base_width": 32, 
        "base_height": 32, 
        "color": (255, 192, 203),  # Розовый
        "health": 200,
        "speed": 3,
        "messages": ["Командообразование!", "Тимбилдинг!", "HR-бренд!"]
    }
}

# Веса для случайного выбора типов
SPAWN_WEIGHTS = {
    1: [80, 15, 5],   # Уровень 1: 5% HR
    2: [70, 20, 10],  # Уровень 2: 10% HR
    3: [60, 25, 15]   # Уровень 3: 15% HR
}

# Модификаторы скорости по уровням
SPEED_MULTIPLIERS = {
    1: 1.0,
    2: 1.4,
    3: 1.8
}

def get_distance(x1, y1, x2, y2):
    """Безопасный расчет расстояния между точками"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) or 1.0  # Избегаем деления на 0

# Звуковые настройки
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
DEFAULT_SOUND_VOLUME = 0.7