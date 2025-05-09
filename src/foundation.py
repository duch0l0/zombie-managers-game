import pygame
from settings import *

class Foundation(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = self._load_image()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.health = 1000
        self.max_health = 1000
        self.concrete_amount = 0  # 0-100%
        self.damage_overlay = pygame.Surface((100, 100), pygame.SRCALPHA)
        
        # Настройки полосы прогресса
        self.progress_height = 10  # Высота полосы
        self.progress_y = 8       # Позиция по Y (вверху)
        self.progress_color = (70, 70, 255)  # Синий цвет заполнения
        self.progress_bg_color = (40, 40, 40)  # Цвет фона полосы
        self.progress_border_color = (100, 100, 100)  # Цвет рамки
        
        # Настройки текста
        self.progress_font = pygame.font.SysFont('Arial', 22, bold=True)
        self.text_color = (200, 200, 255)  # Светло-синий текст
        
    def _load_image(self):
        try:
            image = pygame.image.load(os.path.join(ASSETS_DIR, 'sprites', 'foundation.png')).convert_alpha()
            return pygame.transform.scale(image, (100, 100))
        except:
            print("Изображение фундамента не найдено, будет использован стандартный спрайт")
            surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.rect(surface, (70, 70, 255, 200), (0, 0, 100, 100), border_radius=10)
            return surface

    def update(self):
        self.image = self.original_image.copy()
        
        # Полоса прогресса с рамкой
        if self.concrete_amount > 0:
            # Рамка полосы прогресса
            pygame.draw.rect(self.image, self.progress_border_color, 
                           (0, self.progress_y, 100, self.progress_height), 1)
            
            # Фон полосы (незаполненная часть)
            pygame.draw.rect(self.image, self.progress_bg_color, 
                           (0, self.progress_y, 100, self.progress_height))
            
            # Заполненная часть
            progress_width = 100 * self.concrete_amount / 100
            pygame.draw.rect(self.image, self.progress_color, 
                           (0, self.progress_y, progress_width, self.progress_height))
