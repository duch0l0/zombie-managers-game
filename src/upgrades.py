import pygame
from settings import *
from mixer_truck import MixerTruck

class UpgradeSystem:
    def __init__(self, player, foundation):
        self.player = player
        self.foundation = foundation
        self.points = 0
        self.available_upgrades = {
            "bullet_damage": {
                "name": "Урон",
                "levels": 3,
                "current": 0,
                "cost": [100, 200, 300],
                "effect": lambda lvl: setattr(self.player, 'bullet_damage', 10 + 5 * lvl)
            },
            "concrete_health": {
                "name": "Прочность",
                "levels": 5,
                "current": 0,
                "cost": [150, 250, 400, 600, 800],
                "effect": lambda lvl: (
                    setattr(self.foundation, 'max_health', 1000 + 200 * lvl),
                    setattr(self.foundation, 'health', self.foundation.max_health)
                )
            },
            "mixer_speed": {
                "name": "Скорость МКР",
                "levels": 2,
                "current": 0,
                "cost": [200, 400],
                "effect": lambda lvl: setattr(MixerTruck, 'base_speed', 2.5 + 0.8 * lvl)
            }
        }

    def add_points(self, amount):
        self.points += amount

    def can_upgrade(self, upgrade_id):
        upgrade = self.available_upgrades[upgrade_id]
        return upgrade["current"] < upgrade["levels"] and self.points >= upgrade["cost"][upgrade["current"]]

    def apply_upgrade(self, upgrade_id):
        if not self.can_upgrade(upgrade_id):
            return False

        upgrade = self.available_upgrades[upgrade_id]
        self.points -= upgrade["cost"][upgrade["current"]]
        upgrade["current"] += 1
        upgrade["effect"](upgrade["current"])
        return True

    def draw_menu(self, surface):
        font = pygame.font.SysFont('Arial', 18)
        title = font.render("Улучшения:", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH - 200, 10))

        points_text = font.render(f"Очки: {self.points}", True, GREEN)
        surface.blit(points_text, (SCREEN_WIDTH - 200, 35))

        for i, (upgrade_id, data) in enumerate(self.available_upgrades.items()):
            y_pos = 60 + i * 30
            color = GREEN if self.can_upgrade(upgrade_id) else GRAY
            
            # Название и уровень
            upgrade_text = font.render(
                f"{i+1}. {data['name']} {data['current']}/{data['levels']}",
                True, color
            )
            surface.blit(upgrade_text, (SCREEN_WIDTH - 200, y_pos))
            
            # Стоимость
            if data['current'] < data['levels']:
                cost_text = font.render(
                    f"{data['cost'][data['current']]}", 
                    True, (255, 255, 0)
                )
                surface.blit(cost_text, (SCREEN_WIDTH - 50, y_pos))