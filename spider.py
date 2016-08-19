from time import time
import logging

from gameobject import GameObject, TEAM_ENEMY
from loader import images
from physics import V
from draw_utils import colorize_surface
from spell import EnemySpell
from math_utils import sign, angle90, direction, align, v_from_direction


class Spider(GameObject):
    def __init__(self, **kwargs):
        sprites = [images['spider_right'], images['spider_up'], images['spider_left'], images['spider_down']]
        super(Spider, self).__init__(sprites=sprites, wall=True,
                team=TEAM_ENEMY, **kwargs)
        self.timer_reroute = 2.0

    def attack(self, direction):
        self.direction = direction
        self.speed = V(0, 0)
        bite = SpiderBite(pos=self.pos
                + v_from_direction(self.direction)*32)
        bite.authority = True  # TODO: Um
        self.world.add_object(bite)

    def run(self, seconds):
        self.stunned = max(0, self.stunned - seconds)
        if self.authority:
            self.timer_reroute -= seconds
            if not self.stunned:
                if self.timer_reroute < 0:
                    self.dirty = True
                    self.timer_reroute = 2.0
                    target = self.world.players[0].pos
                    xd = target.x - self.pos.x
                    yd = target.y - self.pos.y
                    if (target - self.pos).magnitude() < 96 and angle90(xd, yd) <  20:
                        logging.info("Attacking!")
                        self.attack(direction(*align(xd, yd)))
                    else:
                        if xd != 0:
                            r = abs(yd/xd)
                            if r < 0.20:
                                yd = 0
                            elif r > 5.0:
                                xd = 0
                        self.speed = V(sign(xd), sign(yd)) * 64
            self.limit_direction_from_delta(*self.speed.tup())
        super(Spider, self).run(seconds)

    def post_run(self):
        # Update which sub-image to use
        self.image_index = int(time() * 5 % len(self.sprites[self.direction]))

    def damage(self, amount):
        super(Spider, self).damage(amount)
        if amount > 0:
            self.stunned += 0.5
            self.dirty = True
            self.speed = V(0, 0)

    def draw(self, screen):
        cx, cy = self.world.camera.topleft
        surface = self.sprites[self.direction][self.image_index]
        if self.stunned > 0:
            surface = colorize_surface(surface, (255, 128, 128, 255))
        screen.blit(surface, self.rect.move((-cx, -cy)))


class SpiderBite(EnemySpell):
    def __init__(self, **kwargs):
        sprites = [images['spell_fire']] * 4
        kwargs['strength'] = kwargs.get('strength', 10)
        kwargs['sprites'] = kwargs.get('sprites', sprites)
        super(SpiderBite, self).__init__(**kwargs)
        self.time_left = 1.0  # Time till spiderbite disappears

    def run(self, seconds):
        super(SpiderBite, self).run(seconds)
        self.time_left -= seconds
        if self.time_left <= 0.0:
            self.damage(99999)


