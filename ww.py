import pygame

from loader import images
from player import Player
from keys import *
from physics import V


class WW(Player):
    def __init__(self, **kwargs):
        sprites = [images['ww_right'], images['ww_up'], images['ww_left'], images['ww_down']]
        kwargs['id'] = kwargs.get('id') or 'w'
        super(WW, self).__init__(sprites, **kwargs)

    def run(self, seconds):
        speed = V(0, 0)
        if K_L in pressed_keys:
            speed += V(1, 0)
        if K_K in pressed_keys:
            speed -= V(0, 1)
        if K_H in pressed_keys:
            speed -= V(1, 0)
        if K_J in pressed_keys:
            speed += V(0, 1)
        self.speed = speed * self.walk_speed
        if speed != V(0, 0):
            self.dirty = True
        super(Player, self).run(seconds)

    def handle(self, event):
        key_dir = {
            K_L: 0,
            K_K: 1,
            K_H: 2,
            K_J: 3
        }
        if event.type == pygame.KEYDOWN:
            if event.key in key_dir:
                self.direction = key_dir[event.key]
                self.sprite = self.sprites[self.direction]
