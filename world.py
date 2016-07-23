from collections import defaultdict
from itertools import chain
    

import pygame

from ww import WW
from witch import Witch
from player import Player
from quadtree import Quadtree
from physics import V


# TODO: Rename to World
class World(object):
    def __init__(self, w, h):
        self.rect = pygame.Rect(0, 0, w, h)
        self.layers = defaultdict(lambda: list())
        self.objs = dict()  # By id
        self.walls = list()
        self.creatures = list()
        self.players = list()
        self.authority = list()  # All objects owned by this client
        self.ww = None
        self.witch = None
        self.cat = None
        self.camera = V(0, 0)
        self.qt = Quadtree(64, 64)
        # self.qt_wall = Quadtree(64, 64) TODO
        # self.qt_enemies = Quadtree(64*4, 64*4)
        # self.qt_general = Quadtree(64*4, 64*4)
        self.objects_to_remove = list()  # Removed after validate()

    def add_object(self, gameobj):
        self.layers[gameobj.depth].append(gameobj)
        self.objs[gameobj.id] = gameobj
        self.qt.add(gameobj)
        if gameobj.wall:
            self.walls.append(gameobj)
        if gameobj.authority:
            self.authority.append(gameobj)
        if isinstance(gameobj, Player):
            self.creatures.append(gameobj)
            self.players.append(gameobj)
        if isinstance(gameobj, WW):
            self.ww = gameobj
        if isinstance(gameobj, Witch):
            self.witch = gameobj
        gameobj.world = self

    def remove_object(self, gameobj):
        self.layers[gameobj.depth].remove(gameobj)
        del self.objs[gameobj.id]
        self.qt.remove(gameobj)
        if gameobj.wall:
            self.walls.remove(gameobj)
        if gameobj.authority:
            self.authority.remove(gameobj)
        if isinstance(gameobj, Player):
            self.creatures.append(gameobj)
            self.players.append(gameobj)
        if isinstance(gameobj, WW):
            self.ww = None
        if isinstance(gameobj, Witch):
            self.witch = None
        gameobj.world = None

    def handle(self, event):
        for obj in self.players:
            obj.handle(event)

    def run(self, seconds):
        for obj in chain(*self.layers.values()):
            obj.run(seconds)

    def post_run(self):
        for obj in chain(*self.layers.values()):
            obj.post_run()

    def validate(self):
        for obj in self.authority:
            obj.validate()
        for obj in self.objects_to_remove:
            self.remove_object(obj)
        self.objects_to_remove = list()

    def draw(self, screen):
        if self.players:
            self.camera = screen.get_rect()
            self.camera.center = self.players[0].pos.tup()

        objects_to_draw = self.qt.collide_rect(self.camera)
        objects_to_draw = sorted(objects_to_draw, key=lambda obj: (obj.depth, obj.pos.y))
        for obj in objects_to_draw:
            obj.draw(screen)

        # for depth, layer in sorted(self.layers.items()):
        #     for obj in sorted(layer, key=lambda o: o.pos.y):
        #         obj.draw(screen)

