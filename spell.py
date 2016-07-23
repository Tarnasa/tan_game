from time import time

from gameobject import GameObject, Static
from loader import images
from network import send_message, send_move_message


class PlayerSpell(GameObject):
    def __init__(self, **kwargs):
        self.strength = 1
        kwargs['health'] = kwargs.get('health', 1)
        super(PlayerSpell, self).__init__(**kwargs)

    def move(self, delta):
        self.world.qt.remove(self)
        self.pos += delta
        self.rect = self.aligned_rect()
        self.world.qt.add(self)

    def post_run(self):
        if self.authority:
            already_collided = set()
            for obj in self.collide_all():
                if obj not in already_collided:
                    if self.collide(obj):
                        send_move_message(self)
                        send_move_message(obj)
                        send_message('L{0}:{1}'.format(self.id, obj.id))
                        already_collided.add(obj)
        self.image_index = int(time() * 6 % len(self.sprites[self.direction]))

    def collide(self, obj):
        """
        Called for all objects this object collides with,
        Return true to indicate that a network message should be sent
        """
        if obj.is_enemy:
            obj.damage(self.strength)
            direction = (obj.pos - self.pos).normalized()
            obj.apply_force(direction * (self.strength / 4.0))
            self.damage(99999)
            return True
        elif obj.wall and isinstance(obj, Static):  # TODO: Better wall check
            self.damage(99999)
            return True
        return False


class PlayerFireball(PlayerSpell):
    def __init__(self, **kwargs):
        sprites = [images['spell_fire']] * 4
        kwargs['strength'] = kwargs.get('strength', 50)
        super(PlayerFireball, self).__init__(sprites=sprites, **kwargs)
