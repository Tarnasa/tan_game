from loader import images
from player import Player


class Witch(Player):
    def __init__(self, **kwargs):
        sprites = [images['witch_right'], images['witch_up'], images['witch_left'], images['witch_down']]
        kwargs['id'] = kwargs.get('id') or 'e'
        super(Witch, self).__init__(sprites, **kwargs)
