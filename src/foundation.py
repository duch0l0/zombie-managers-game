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
        
        # Индикатор бетона (серый)
        if self.concrete_amount > 0:
            progress = pygame.Surface((100 * self.concrete_amount/100, 100), pygame.SRCALPHA)
            progress.fill((100, 100, 100, 180))
            self.image.blit(progress, (0, 0))
        
        # Индикатор повреждений (красный)
        damage_alpha = int(200 * (1 - self.health/self.max_health))
        if damage_alpha > 0:
            self.damage_overlay.fill((255, 0, 0, damage_alpha))
            self.image.blit(self.damage_overlay, (0, 0))