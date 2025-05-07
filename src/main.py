import os
import sys
import pygame
import random
from settings import *
from player import Player
from zombie import ZombieManager
from mixer_truck import MixerTruck
from foundation import Foundation
from upgrades import UpgradeSystem

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Zombie Managers vs Concrete Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Игровые объекты
        self.foundation = Foundation()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.mixers = pygame.sprite.Group()
        
        # Добавление объектов
        self.all_sprites.add(self.foundation, self.player)
        
        # Система уровней
        self.current_level = 1
        self.zombies_killed = 0
        self.zombie_spawn_timer = 0
        self.zombie_spawn_interval = LEVELS[self.current_level]["zombie_spawn_rate"]
        
        # Система улучшений
        self.upgrade_system = UpgradeSystem(self.player, self.foundation)
        self.show_upgrades = False
        self.notification = None
        
        # Таймеры
        self.mixer_spawn_timer = 0
        self.mixer_spawn_interval = FPS * 10  # 10 секунд
        
        # Первый миксер
        self.spawn_mixer()

    def spawn_mixer(self):
        mixer = MixerTruck()
        mixer.set_target(self.foundation)
        self.all_sprites.add(mixer)
        self.mixers.add(mixer)

    def spawn_zombie(self):
        if len(self.zombies) >= LEVELS[self.current_level]["max_zombies"]:
            return
            
        side = random.randint(0, 3)
        if side == 0:  # Верх
            x = random.randint(0, SCREEN_WIDTH)
            y = -30
        elif side == 1:  # Право
            x = SCREEN_WIDTH + 30
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Низ
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 30
        else:  # Лево
            x = -30
            y = random.randint(0, SCREEN_HEIGHT)
        
        zombie = ZombieManager(x, y, random.choice(["manager", "marketing", "hr"]))
        self.all_sprites.add(zombie)
        self.zombies.add(zombie)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.player.shoot(mouse_x, mouse_y)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    self.show_upgrades = not self.show_upgrades
                elif self.show_upgrades:
                    if event.key == pygame.K_1:
                        if self.upgrade_system.apply_upgrade("bullet_damage"):
                            self._show_notification("Урон пуль +!")
                    elif event.key == pygame.K_2:
                        if self.upgrade_system.apply_upgrade("concrete_health"):
                            self._show_notification("Прочность +!")
                    elif event.key == pygame.K_3:
                        if self.upgrade_system.apply_upgrade("mixer_speed"):
                            self._show_notification("Скорость МКР +!")
                            for mixer in self.mixers:
                                mixer.speed = MixerTruck.base_speed

    def _show_notification(self, message):
        """Показывает уведомление над фундаментом"""
        font = pygame.font.SysFont('Arial', 48, bold=True)
        text = font.render(message, True, (255, 215, 0))  # Золотой цвет
        
        # Позиция над фундаментом
        notification_y = self.foundation.rect.top - 80
        if notification_y < 20:  # Не выходить за верх экрана
            notification_y = 20
        
        self.notification = {
            "text": text,
            "rect": pygame.Rect(
                SCREEN_WIDTH//2 - text.get_width()//2,
                notification_y,
                text.get_width(),
                text.get_height()
            ),
            "timer": 90  # 1.5 секунды
        }

    def update(self):
        if self.show_upgrades:
            return
            
        # Спавн зомби
        self.zombie_spawn_timer += 1
        if self.zombie_spawn_timer >= self.zombie_spawn_interval:
            self.spawn_zombie()
            self.zombie_spawn_timer = 0
        
        # Спавн миксеров
        self.mixer_spawn_timer += 1
        if self.mixer_spawn_timer >= self.mixer_spawn_interval:
            self.spawn_mixer()
            self.mixer_spawn_timer = 0
        
        # Обработка столкновений
        self._handle_collisions()
        
        # Обновление объектов
        self.all_sprites.update()
        self.player.bullets.update()
        
        # Обновление уведомлений
        if self.notification:
            self.notification["timer"] -= 1
            if self.notification["timer"] <= 0:
                self.notification = None

    def _handle_collisions(self):
        # Пули vs зомби
        for bullet in self.player.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.zombies, True)
            if hits:
                bullet.kill()
                self.zombies_killed += len(hits)
                self.upgrade_system.add_points(10 * len(hits))
                
                if self.zombies_killed >= LEVELS[self.current_level]["required_kills"]:
                    self.next_level()
        
        # Зомби vs фундамент
        for zombie in self.zombies:
            if pygame.sprite.collide_rect(zombie, self.foundation):
                self.foundation.health -= 10
                zombie.kill()

    def next_level(self):
        if self.current_level >= len(LEVELS):
            self._show_notification("ПОБЕДА!")
            return
            
        self.current_level += 1
        self.zombies_killed = 0
        self.zombie_spawn_interval = LEVELS[self.current_level]["zombie_spawn_rate"]
        self._show_notification(f"УРОВЕНЬ {self.current_level}!")

    def draw(self):
        self.screen.fill(BLACK)
        
        # 1. Отрисовка игровых объектов
        self.all_sprites.draw(self.screen)
        self.player.bullets.draw(self.screen)
        
        # 2. Оповещения (поверх объектов)
        if self.notification:
            alpha = min(255, self.notification["timer"] * 3)
            self.notification["text"].set_alpha(alpha)
            
            # Фон для лучшей читаемости
            bg_rect = self.notification["rect"].inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, alpha//2), bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 215, 0, alpha//3), bg_rect, 2, border_radius=5)
            
            self.screen.blit(self.notification["text"], self.notification["rect"])
        
        # 3. Сообщения зомби
        for zombie in self.zombies:
            zombie.draw_message(self.screen)
        
        # 4. Интерфейс
        self._draw_ui()
        
        # 5. Меню улучшений (самое верхнее)
        if self.show_upgrades:
            self._draw_upgrade_menu()
        
        pygame.display.flip()

    def _draw_ui(self):
        info = [
            f"Уровень: {self.current_level}",
            f"Убито: {self.zombies_killed}/{LEVELS[self.current_level]['required_kills']}",
            f"Очки: {self.upgrade_system.points}",
            f"Опалубка: {self.foundation.health}/{self.foundation.max_health}"
        ]
        
        for i, text in enumerate(info):
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (10, 10 + i * 25))

    def _draw_upgrade_menu(self):
        overlay = pygame.Surface((220, 150), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (SCREEN_WIDTH - 230, 10))
        self.upgrade_system.draw_menu(self.screen)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()