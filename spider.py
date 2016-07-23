from time import time

from gameobject import GameObject
from loader import images
from physics import V
from draw_utils import colorize_surface


class Spider(GameObject):
    def __init__(self, **kwargs):
        sprites = [images['spider_right'], images['spider_up'], images['spider_left'], images['spider_down']]
        super(Spider, self).__init__(sprites=sprites, wall=True, is_enemy=True, **kwargs)
        self.timer_reroute = 2.0

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
                    if xd != 0:
                        r = abs(yd/xd)
                        if r < 0.20:
                            yd = 0
                        elif r > 5:
                            xd = 0
                    def sign(x):  # Because copysign is stupid
                        return int(x > 0) - int(x < 0)
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

