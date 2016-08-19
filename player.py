import pygame

from gameobject import GameObject, TEAM_PLAYER
from keys import *
from physics import V
from spell import PlayerFireball
from network import send_create_message


class Player(GameObject):
    def __init__(self, sprites, **kwargs):
        super(Player, self).__init__(sprites=sprites, wall=True,
                team=TEAM_PLAYER, **kwargs)
        self.walk_speed = 64*5

    def run(self, seconds):
        if self.authority:
            previous_speed = self.speed.copy()
            speed = V(0, 0)
            if K_RIGHT in pressed_keys:
                speed += V(1, 0)
            if K_UP in pressed_keys:
                speed -= V(0, 1)
            if K_LEFT in pressed_keys:
                speed -= V(1, 0)
            if K_DOWN in pressed_keys:
                speed += V(0, 1)
            self.speed = speed * self.walk_speed
            if self.speed != previous_speed:
                self.dirty = True
            # players send ALL the things
            self.dirty = True
        else:
            # therefore they don't even NEED speed
            self.speed = V(0, 0)
        super(Player, self).run(seconds)

    def move(self, d):
        prev = self.rect.copy()
        super(Player, self).move(d)
        # Update sprite
        if prev != self.rect:
            xd = self.rect.left - prev.left
            yd = self.rect.top - prev.top
            self.limit_direction_from_delta(xd, yd)

    def handle(self, event):
        if self.authority:
            key_dir = {
                K_RIGHT: 0,
                K_UP: 1,
                K_LEFT: 2,
                K_DOWN: 3
            }
            if event.type == pygame.KEYDOWN:
                if event.key in key_dir:
                    self.direction = key_dir[event.key]
                elif event.key == K_SPACE:
                    speed = [V(1, 0), V(0, -1), V(-1, 0), V(0, 1)][self.direction] * 64*4
                    spell = PlayerFireball(pos=self.pos.copy(), direction=self.direction,
                                           speed=speed, authority=True)
                    self.world.add_object(spell)
                    send_create_message(spell)
