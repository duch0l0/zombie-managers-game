import os
import sys
import pygame
import random
import math
from settings import *
from player import Player
from zombie import ZombieManager
from mixer_truck import MixerTruck
from foundation import Foundation
from upgrades import UpgradeSystem
from sounds import SoundSystem

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
        
        # Система частиц
        self.particles = []
        
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

        self.sound = SoundSystem()
        self.sound_enabled = True
        self.debug_mode = False  # Режим отладки (показ хитбоксов)

    def spawn_mixer(self):
        mixer = MixerTruck()
        mixer.set_target(self.foundation)
        self.all_sprites.add(mixer)
        self.mixers.add(mixer)
        self._create_sparks(mixer.rect.center, (255, 200, 100), 30)

    def spawn_zombie(self):
        if len(self.zombies) >= LEVELS[self.current_level]["max_zombies"]:
            return
            
        side = random.randint(0, 3)
        if side == 0:  # Верх
            x = random.randint(0, SCREEN_WIDTH)
            y = -50
        elif side == 1:  # Право
            x = SCREEN_WIDTH + 50
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Низ
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 50
        else:  # Лево
            x = -50
            y = random.randint(0, SCREEN_HEIGHT)
        
        # Выбор типа зомби с учетом весов
        weights = SPAWN_WEIGHTS[self.current_level]
        zombie_type = random.choices(["manager", "marketing", "hr"], weights=weights)[0]
        
        zombie = ZombieManager(x, y, zombie_type)
        zombie.foundation = self.foundation  # Ссылка на фундамент
        self.all_sprites.add(zombie)
        self.zombies.add(zombie)

    def _create_sparks(self, pos, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 3)
            self.particles.append({
                "x": pos[0], "y": pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": color,
                "life": random.randint(20, 40),
                "size": random.uniform(1, 4)
            })

    def _create_ring(self, pos, color, radius=30):
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            self.particles.append({
                "x": pos[0], "y": pos[1],
                "vx": math.cos(rad) * 1.5,
                "vy": math.sin(rad) * 1.5,
                "color": color,
                "life": 50,
                "size": 2,
                "growing": True,
                "max_size": radius
            })

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
                
                if self.player.bullet_damage > 15:
                    self._create_sparks((mouse_x, mouse_y), (255, 100, 0), 15)
                
                if self.sound_enabled:
                    self.sound.play('shot')
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    self.show_upgrades = not self.show_upgrades
                elif event.key == pygame.K_F1:  # Переключение режима отладки
                    self.debug_mode = not self.debug_mode
                elif self.show_upgrades:
                    if event.key == pygame.K_1:
                        if self.upgrade_system.apply_upgrade("bullet_damage"):
                            self._show_notification("Урон пуль +!")
                            self._create_sparks(self.player.rect.center, (255, 100, 0), 30)
                    elif event.key == pygame.K_2:
                        if self.upgrade_system.apply_upgrade("concrete_health"):
                            self._show_notification("Прочность +!")
                            self._create_ring(self.foundation.rect.center, (0, 200, 255), 50)
                    elif event.key == pygame.K_3:
                        if self.upgrade_system.apply_upgrade("mixer_speed"):
                            self._show_notification("Скорость МКР +!")
                            for mixer in self.mixers:
                                mixer.speed = MixerTruck.base_speed
                                self._create_sparks(mixer.rect.center, (255, 200, 100), 20)

    def _show_notification(self, message):
        font = pygame.font.SysFont('Arial', 48, bold=True)
        text = font.render(message, True, (255, 215, 0))
        notification_y = max(20, self.foundation.rect.top - 80)
        
        self.notification = {
            "text": text,
            "rect": pygame.Rect(
                SCREEN_WIDTH//2 - text.get_width()//2,
                notification_y,
                text.get_width(),
                text.get_height()
            ),
            "timer": 90
        }

    def update(self):
        if self.show_upgrades:
            return
            
        # Обновление частиц
        for p in self.particles[:]:
            if p.get("growing", False):
                p["size"] += 0.2
                if "max_size" in p and p["size"] > p["max_size"]:
                    p["growing"] = False
            else:
                p["size"] *= 0.98
            
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            
            if p["life"] <= 0:
                self.particles.remove(p)
        
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
        # Пули vs зомби (с проверкой hitbox)
        for bullet in self.player.bullets:
            hits = []
            for zombie in self.zombies:
                if bullet.rect.colliderect(zombie.hitbox):
                    hits.append(zombie)
            
            if hits:
                bullet.kill()
                if self.sound_enabled:
                    self.sound.play('hit', volume=0.5)
                
                self.zombies_killed += len(hits)
                self.upgrade_system.add_points(10 * len(hits))
                
                for zombie in hits:
                    # Эффект попадания
                    for _ in range(10):
                        self.particles.append({
                            "x": zombie.rect.centerx,
                            "y": zombie.rect.centery,
                            "vx": random.uniform(-2, 2),
                            "vy": random.uniform(-2, 2),
                            "color": (255, 50, 0),
                            "life": random.randint(15, 30),
                            "size": random.uniform(2, 4)
                        })
                    zombie.kill()
                
                if self.zombies_killed >= LEVELS[self.current_level]["required_kills"]:
                    self.next_level()

    def next_level(self):
        if self.current_level >= len(LEVELS):
            self._show_notification("ПОБЕДА!")
            return
            
        self.current_level += 1
        self.zombies_killed = 0
        self.zombie_spawn_interval = LEVELS[self.current_level]["zombie_spawn_rate"]
        
        self._show_notification(f"УРОВЕНЬ {self.current_level}!")
        self._create_ring(self.foundation.rect.center, (100, 255, 100), 70)

    def draw(self):
        self.screen.fill(BLACK)
        
        # Отрисовка игровых объектов
        self.all_sprites.draw(self.screen)
        self.player.bullets.draw(self.screen)
        
        # Отрисовка частиц
        for p in self.particles:
            alpha = min(255, p["life"] * 6)
            color = (*p["color"], alpha) if isinstance(p["color"], tuple) else p["color"] + (alpha,)
            pygame.draw.circle(
                self.screen, color,
                (int(p["x"]), int(p["y"])),
                int(p["size"])
            )
        
        # Отрисовка сообщений зомби
        for zombie in self.zombies:
            zombie.draw_message(self.screen)
        
        # Режим отладки (хитбоксы)
        if self.debug_mode:
            for zombie in self.zombies:
                pygame.draw.rect(self.screen, (255, 0, 0), zombie.hitbox, 1)
            pygame.draw.rect(self.screen, (0, 255, 0), self.player.rect, 1)
        
        # Оповещения
        if self.notification:
            alpha = min(255, self.notification["timer"] * 3)
            bg_rect = self.notification["rect"].inflate(30, 15)
            pygame.draw.rect(self.screen, (0, 0, 0, alpha//2), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 215, 0, alpha//3), bg_rect, 3, border_radius=10)
            self.notification["text"].set_alpha(alpha)
            self.screen.blit(self.notification["text"], self.notification["rect"])
        
        # Интерфейс
        self._draw_ui()
        
        # Меню улучшений
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