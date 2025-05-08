import pygame
import os
from settings import ASSETS_DIR

class SoundSystem:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {
            'shot': self._load_sound('shot_sounds.wav'),
            'hit': self._load_sound('zombie_hit.wav')
        }
    
    def _load_sound(self, filename):
        """Загрузка звука с проверкой ошибок"""
        try:
            path = os.path.join(ASSETS_DIR, 'sounds', filename)
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Ошибка загрузки звука {filename}: {e}")
            return None
    
    def play(self, sound_name, volume=0.7):
        """Проигрывание звука с настройкой громкости"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()