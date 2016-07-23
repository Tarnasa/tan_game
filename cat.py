from loader import images
from player import Player
from physics import V
from time import time


class Cat(Player):
    def __init__(self, **kwargs):
        sprites = images['cat_sit']
        kwargs['id'] = kwargs.get('id') or 'c'
        super(Cat, self).__init__(sprites, **kwargs)

    def post_run(self):
        super(Cat, self).post_run()
        if self.speed != V(0, 0):
            self.sprites = images['cat_walk']
        else:
            self.sprites = images['cat_sit']
        self.image_index = int(time() * 5 % len(self.sprites[self.direction]))
