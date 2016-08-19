from math import copysign

import pygame

from physics import V
from identifier import get_new_id
from network import send_message, send_move_message
import network

TEAM_NEUTRAL, TEAM_PLAYER, TEAM_ENEMY = range(3)


class GameObject(object):
    """ The base class for hopefully all objects in the game """
    def __init__(self, sprites=None, id=None, **kwargs):
        self.sprites = sprites
        if sprites.__class__.__name__ == 'Surface':
            self.sprites = [[self.sprites], [self.sprites], [self.sprites], [self.sprites]]
        if self.sprites[0].__class__.__name__ == 'Surface':
            self.sprites = [[sprite] for sprite in self.sprites]
        # Defaults
        self.health = 100
        self.direction = 3
        self.wall = False
        self.depth = 0
        self.pos = V(0, 0)
        self.speed = V(0, 0)
        self.team = TEAM_NEUTRAL
        self.image_index = 0
        self.authority = False  # This client does not own this object
        self.world = None
        self.dirty = False  # Position needs to be sent to other players
        self.stunned = 0  # Seconds left till not stunned
        self.force = V(0, 0)
        self.decel = 16
        # Apply remaining keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.mask = self.sprites[self.direction][0]
        self.rect = self.mask.get_rect()
        self.rect = self.aligned_rect()
        if id is None:
            self.id = network.character + str(get_new_id())
        else:
            self.id = id

    def aligned_rect(self, pos=None):
        """ Calculates the best pixel-position for the rect """
        pos = pos or self.pos
        new_rect = self.rect.copy()
        new_rect.center = (int(pos.x + 0.5), int(pos.y + 0.5))
        return new_rect

    def set_topleft(self, pos):
        """ Set the top-left pixel-position, and update everything else """
        self.world.qt.remove(self)
        self.rect.topleft = pos
        self.pos = V(*self.rect.center)
        self.world.qt.add(self)

    def run(self, seconds):
        """ Simulate the object's movement for `seconds` """
        collided = False
        if self.wall:
            coll = self.collide_stop()
            if coll:
                if self.authority:
                    self.unstuck_away(4)
                collided = True
        if not collided:
            delta = self.speed * seconds
            # Add on the movement from self.force
            if self.force != V(0, 0):
                accel = self.force.normalized() * -self.decel
                maximum_force_time = self.force.magnitude() / self.decel
                if seconds > maximum_force_time:
                    delta += self.force*seconds - accel*0.5*(seconds**2)
                else:
                    t = maximum_force_time
                    delta += self.force*t - accel*0.5*(t**2)
            # Actually move
            self.move(delta)
        # Reduce the force
        if self.force.magnitude() > self.decel:
            self.force -= self.force.normalized() * self.decel
        else:
            self.force = V(0, 0)
        # delta = self.speed * seconds
        # self.move(delta)

    def post_run(self):
        """ To be implemented in subclasses for code that needs to run after every object has been run() """
        pass

    def move(self, delta):
        """ Apply a delta and check for collisions """
        self.world.qt.remove(self)
        xd, yd = delta
        xs = copysign(1.0, xd)
        ys = copysign(1.0, yd)
        xd = abs(xd)
        yd = abs(yd)
        while xd or yd:
            xc = True
            yc = True
            if xd > 0:
                if xd < 1.0:
                    remaining = copysign(xd, xs)
                    pos_try_x = self.pos + V(remaining, 0)
                    try_x = self.aligned_rect(pos_try_x)
                    xc = self.collide_stop(try_x)
                    if not xc:
                        self.pos = pos_try_x
                        self.rect = try_x
                        xd = 0
                else:
                    try_x = self.rect.move((xs, 0))
                    xc = self.collide_stop(try_x)
                    if not xc:
                        self.pos.x += xs
                        self.rect = try_x
                        xd -= 1
            if yd > 0:
                if yd < 1.0:
                    remaining = copysign(yd, ys)
                    pos_try_y = self.pos + V(0, remaining)
                    try_y = self.aligned_rect(pos_try_y)
                    yc = self.collide_stop(try_y)
                    if not yc:
                        self.pos = pos_try_y
                        self.rect = try_y
                        yd = 0
                else:
                    try_y = self.rect.move((0, ys))
                    yc = self.collide_stop(try_y)
                    if not yc:
                        self.pos.y += ys
                        self.rect = try_y
                        yd -= 1
            if xc and yc:
                break
        self.world.qt.add(self)

    def unstuck_away(self, max_distance):
        """Try moving the object away from all currently colliding objects till no longer stuck"""
        self.world.qt.remove(self)
        away_from_stuck = V(0, 0)
        for obj in self.world.qt.collide_rect(self.rect):
            if self.is_stopped_by(obj):
                delta = self.pos - obj.pos
                r2 = delta.r2()
                if r2:
                    delta /= float(delta.r2())  # Farther objects have less effect on direction
                else:
                    delta += V(1.0, 0.0)
                away_from_stuck += delta
        if away_from_stuck != V(0, 0):
            away_from_stuck = away_from_stuck.normalized()
            try_rect = self.rect
            for distance in range(max_distance + 1):
                try_rect = self.rect.move(*(away_from_stuck * distance).tup())
                coll = self.collide_stop(try_rect)
                if not coll:
                    break
            self.rect = try_rect
            self.pos = V(*self.rect.center)
            self.dirty = True
        self.world.qt.add(self)

    def set_pos(self, pos):
        """ Set the position of the object safely """
        self.world.qt.remove(self)
        self.pos = pos
        self.rect = self.aligned_rect()
        self.world.qt.add(self)

    def limit_direction_from_delta(self, xd, yd):
        """
        If the object is moving in a cardinal direction, make sure it is facing that way,
        If the object is moving diagonally, then make sure it is facing in at least one of it's component directions
        """
        if xd == 0 and yd == 0:
            return
        directions = []
        if xd > 0:
            directions.append(0)
        elif xd < 0:
            directions.append(2)
        if yd > 0:
            directions.append(3)
        elif yd < 0:
            directions.append(1)
        if self.direction not in directions:
            self.direction = directions[0]

    def collide_stop(self, rect=None):
        """ Returns a stopping object that this object is colliding with, or None """
        rect = rect or self.rect
        for obj in self.world.qt.collide_rect(rect):
            if obj is not self and self.is_stopped_by(obj):
                return obj

    def is_stopped_by(self, obj):
        """ Returns whether the given object should stop this object's movement """
        return obj.wall

    def collide_all(self, rect=None):
        """ Iterates over all object which are currently colliding with this one """
        rect = rect or self.rect
        for obj in self.world.qt.collide_rect(rect):
            if obj is not self:
                yield obj

    def apply_force(self, force):
        """Applies a rapidly decaying impulse to the given object, miving it"""
        self.force += force
        # if self.authority:
        #     send_message("F{0}:{1}:{2}".format(self.id, self.force.x, self.force.y))

    def damage(self, amount):
        """ Applies the given amount of damage, and checks for death """
        if self.health > 0:
            self.health -= amount
            if self.health <= 0:
                self.health = 0

    def validate(self):
        """ Checks if any actions need to be taken because we are the authority of this object """
        if self.dirty:
            send_move_message(self)
            self.dirty = False
        if self.health <= 0:
            self.world.objects_to_remove.append(self)
            send_message('X{0}'.format(self.id))

    def draw(self, screen):
        """ Draws the gameobject's sprite to the given screen """
        cx, cy = self.world.camera.topleft
        screen.blit(self.sprites[self.direction][self.image_index],
                    self.rect.move((-cx, -cy)))


class Static(GameObject):
    def __init__(self, **kwargs):
        super(Static, self).__init__(**kwargs)

    def run(self, seconds):
        pass





    def old_move(self, delta):
        """ Apply a delta and check for collisions """
        self.world.qt.remove(self)
        new_rect = self.aligned_rect(self.pos + delta.x_part())
        if not self.collide_stop(new_rect):
            self.pos += delta.x_part()
            self.rect = new_rect
        new_rect = self.aligned_rect(self.pos + delta.y_part())
        if not self.collide_stop(new_rect):
            self.pos += delta.y_part()
            self.rect = new_rect
        self.world.qt.add(self)

    def unstuck_shake(self, max_distance):
        """Try moving the object to nearby positions until it is on longer overlapping a wall"""
        self.world.qt.remove(self)
        try_rect = self.rect
        for distance in range(max_distance):
            for offset in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
                try_rect = self.rect.move(offset)
                coll = self.collide_stop(try_rect)
                if not coll:
                    break
            else:
                continue
            break
        self.rect = try_rect
        self.pos = V(*self.rect.center)
        self.world.qt.add(self)

