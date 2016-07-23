import logging
import StringIO

import pygame
from PIL import Image


def load_image(filename):
    logging.debug('Loading image from {0}'.format(filename))
    surface = pygame.image.load(filename)
    surface.set_colorkey((255, 255, 255))
    surface = surface.convert_alpha()
    rect = surface.get_rect()
    surface = pygame.transform.scale(surface, (rect.width * 8, rect.height * 8))
    return surface


def load_strip(filename, w, h):
    logging.debug('Loading image strip from {0} with w/h of {1}/{2}'.format(filename, w, h))
    surface = pygame.image.load(filename)
    surface.set_colorkey((255, 255, 255))
    surface = surface.convert_alpha()
    rect = surface.get_rect()
    surface = pygame.transform.scale(surface, (rect.width * 8, rect.height * 8))
    w *= 8
    h *= 8
    surfaces = list()
    for y in range(0, surface.get_height(), h):
        for x in range(0, surface.get_width(), w):
            sub = surface.subsurface(pygame.Rect(x, y, w, h))
            surfaces.append(sub)
    logging.debug('Found {0} sub-images in strip'.format(len(surfaces)))
    return surfaces


def load_gif(filename):
    logging.debug('Loading GIF from {0}'.format(filename))
    img = Image.open(filename)
    palette = img.palette
    surfaces = list()
    try:
        while True:
            new_img = Image.new('RGB', img.size)
            new_img.paste(img)

            buf = StringIO.StringIO()
            new_img.save(buf, 'PNG')
            buf.seek(0)
            surface = pygame.image.load(buf, '.png')
            surface.set_colorkey((255, 255, 255))
            surface = surface.convert_alpha()
            rect = surface.get_rect()
            surface = pygame.transform.scale(surface, (rect.width * 8, rect.height * 8))
            surfaces.append(surface)

            img.seek(img.tell() + 1)
    except EOFError:
        pass  # Done reading frames
    return surfaces

images = dict()
fonts = dict()


def load_all():
    images['witch_down'] = load_image('images/evil_witch_down.png')
    images['witch_left'] = load_image('images/evil_witch_left.png')
    images['witch_right'] = pygame.transform.flip(load_image('images/evil_witch_left.png'), True, False)
    images['witch_up'] = load_image('images/evil_witch_up.png')

    images['ww_right'] = load_image('images/werewolf_right.png')
    images['ww_up'] = load_image('images/werewolf_up.png')
    images['ww_left'] = load_image('images/werewolf_left.png')
    images['ww_down'] = load_image('images/werewolf_down.png')

    images['cat_up'], images['cat_down'], images['cat_right'], images['cat_left'] = load_strip('images/cat.png', 8, 8)
    images['cat'] = load_strip('images/cat2.png', 8, 8)
    images['cat_sit'] = [[img] for img in images['cat'][:4]]
    images['cat_walk'] = [images['cat'][i:i+2] for i in range(4, 12, 2)]

    images['grass1'] = load_image('images/grass_floor1.png')
    images['grass2'] = load_image('images/grass_floor2.png')
    images['bush'] = load_image('images/grass_bush.png')

    images['red_tiles'] = load_strip('images/tile_reddungeon.png', 8, 8)
    images['red_brick_floor'] = images['red_tiles'][0]

    images['spider_right'] = load_strip('images/spider_right.png', 8, 8)
    images['spider_up'] = load_strip('images/spider_up.png', 8, 8)
    images['spider_left'] = load_strip('images/spider_left.png', 8, 8)
    images['spider_down'] = load_strip('images/spider_down.png', 8, 8)

    images['spell_fire'] = load_gif('images/spell_fire.gif')

    fonts['select'] = pygame.font.Font('fonts/YatraOne-Regular.ttf', 32)
    fonts['chat'] = pygame.font.Font('fonts/YatraOne-Regular.ttf', 24)


