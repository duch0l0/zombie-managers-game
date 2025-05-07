import os
import sys
import pygame
import random
from settings import *
from player import Player
from zombie import ZombieManager
from mixer_truck import MixerTruck
from foundation import Foundation

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Zombie Managers vs Concrete Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Игровые группы
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        
        # Игровые объекты
        self.foundation = Foundation()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.mixer_truck = MixerTruck()
        self.mixer_truck.set_target(self.foundation)
        
        # Добавляем объекты в группы
        self.all_sprites.add(self.foundation)
        self.all_sprites.add(self.mixer_truck)
        self.all_sprites.add(self.player)
        
        # Система уровней
        self.current_level = 1
        self.zombies_killed = 0
        self.zombie_spawn_timer = 0
        self.zombie_spawn_interval = LEVELS[self.current_level]["zombie_spawn_rate"]
        self.mixer_spawn_timer = 0
        self.mixer_spawn_interval = FPS * 10

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
        
        zombie_type = random.choices(
            ["manager", "marketing", "hr"],
            weights=[70, 20, 10],
            k=1
        )[0]
        
        zombie = ZombieManager(x, y, zombie_type)
        self.all_sprites.add(zombie)
        self.zombies.add(zombie)

    def next_level(self):
        if self.current_level >= len(LEVELS):
            print("Поздравляем! Вы прошли все уровни!")
            return
            
        self.current_level += 1
        self.zombies_killed = 0
        self.zombie_spawn_interval = LEVELS[self.current_level]["zombie_spawn_rate"]
        
        # Анимация перехода уровня
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for alpha in range(0, 255, 10):
            overlay.fill((0, 0, 0, alpha))
            self.draw()
            self.screen.blit(overlay, (0, 0))
            
            font = pygame.font.SysFont('Arial', 72, bold=True)
            text = font.render(f"Уровень {self.current_level}!", True, (255, 215, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            pygame.time.delay(30)

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

    def update(self):
        # Спавн зомби
        self.zombie_spawn_timer += 1
        if self.zombie_spawn_timer >= self.zombie_spawn_interval:
            self.spawn_zombie()
            self.zombie_spawn_timer = 0
        
        # Спавн миксеров
        self.mixer_spawn_timer += 1
        if self.mixer_spawn_timer >= self.mixer_spawn_interval:
            mixer = MixerTruck()
            mixer.set_target(self.foundation)
            self.all_sprites.add(mixer)
            self.mixer_spawn_timer = 0
        
        # Проверка столкновений пуль с зомби
        for bullet in self.player.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.zombies, True)
            if hits:
                bullet.kill()
                self.zombies_killed += len(hits)
                
                # Проверка перехода уровня
                if self.zombies_killed >= LEVELS[self.current_level]["required_kills"]:
                    self.next_level()
        
        # Проверка столкновений зомби с фундаментом
        for zombie in self.zombies:
            if pygame.sprite.collide_rect(zombie, self.foundation):
                self.foundation.health -= 10
                zombie.kill()
        
        self.all_sprites.update()
        self.player.bullets.update()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Отрисовка всех спрайтов
        self.all_sprites.draw(self.screen)
        self.player.bullets.draw(self.screen)
        
        # Отрисовка сообщений зомби
        for zombie in self.zombies:
            zombie.draw_message(self.screen)
        
        # Интерфейс
        debug_info = [
            f"Уровень: {self.current_level}",
            f"Убито: {self.zombies_killed}/{LEVELS[self.current_level]['required_kills']}",
            f"Опалубка: {self.foundation.health}/{self.foundation.max_health}",
            f"Бетон: {self.foundation.concrete_amount}%"
        ]
        
        for i, text in enumerate(debug_info):
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()