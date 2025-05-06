import os
import sys
import pygame
import random
from settings import *
from player import Player
from zombie import ZombieManager
from mixer_truck import MixerTruck
from foundation import Foundation

# Добавляем текущую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Zombie Managers vs Concrete Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Шрифт
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()  # Группа для зомби
        self.zombie_spawn_timer = 0
        self.zombie_spawn_interval = 60  # Спавн каждую секунду (при FPS=60)
        
        # Игровые объекты (ПРАВИЛЬНЫЙ ПОРЯДОК ИНИЦИАЛИЗАЦИИ)
        self.foundation = Foundation()
        self.mixer_truck = MixerTruck()
        self.mixer_truck.set_target(self.foundation)  # Устанавливаем
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Связываем объекты
        self.foundation.mixer = self.mixer_truck
        self.mixer_truck.foundation = self.foundation
        
        # Добавляем в группы
        self.all_sprites.add(self.foundation)
        self.all_sprites.add(self.mixer_truck)
        self.all_sprites.add(self.player)
        
        # Таймеры
        self.zombie_spawn_timer = 0
        self.zombie_spawn_interval = 60
        self.mixer_cooldown = 0

        self.mixers = pygame.sprite.Group()
        self.mixer_spawn_timer = 0
        self.mixer_spawn_interval = FPS * 10  # Новая машина каждые 10 секунд

    def spawn_zombie(self):
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
    
        # Создаем зомби и добавляем в группы
        zombie = ZombieManager(x, y)
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
            
            # Обработка клика мыши (только если событие - нажатие кнопки)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.player.shoot(mouse_x, mouse_y)

    def update(self):
        # Спавн новых миксерав
        self.mixer_spawn_timer += 1
        if self.mixer_spawn_timer >= self.mixer_spawn_interval:
            self.spawn_mixer()
            self.mixer_spawn_timer = 0

        # Спавн зомби
        self.zombie_spawn_timer += 1
        if self.zombie_spawn_timer >= self.zombie_spawn_interval:
            self.spawn_zombie()
            self.zombie_spawn_timer = 0
        
        # Управление миксером
        self.mixer_cooldown += 1
        if self.mixer_cooldown >= 300:
            self.mixer_truck.start_pouring()
            self.mixer_cooldown = 0
        
        # Проверка столкновений
        for zombie in self.zombies:
            if pygame.sprite.collide_rect(zombie, self.foundation):
                self.foundation.health -= 1
                zombie.kill()
        
        if random.random() < 0.01:  # 1% шанс каждый кадр
            self.mixer_truck.start_pouring()
        
        self.all_sprites.update()

        # Проверка столкновений пуль с зомби
        for bullet in self.player.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.zombies, True)  # True - удалять зомби
            if hits:
                bullet.kill()
                print(f"Убито зомби! Осталось: {len(self.zombies)}")
        
        # Обновление пуль
        if hasattr(self.player, 'bullets'):
            self.player.bullets.update()
            # Проверка столкновений
            for bullet in self.player.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.zombies, True)
                if hits:
                    bullet.kill()
    
    def spawn_mixer(self):
        mixer = MixerTruck()
        mixer.foundation = self.foundation
        self.mixers.add(mixer)
        self.all_sprites.add(mixer)

    def draw(self):
        self.screen.fill(BLACK)
        
        # Отрисовка всех спрайтов
        self.all_sprites.draw(self.screen)
            
        # Отрисовка пуль
        if hasattr(self.player, 'bullets'):
            self.player.bullets.draw(self.screen)
        
        # Отрисовка интерфейса
        debug_info = [
            f"Опалубка: {self.foundation.health}/{self.foundation.max_health}",
            f"Бетон: {self.foundation.concrete_amount}%",
            f"Зомби: {len(self.zombies)}",
            f"Миксер: {'Заливка' if self.mixer_truck.pouring else 'Движение'}"
        ]
        
        for i, text in enumerate(debug_info):
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()