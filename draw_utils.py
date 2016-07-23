import pygame

from utils import memoize, memoize_with


@memoize
def text_to_surface(text, color, font):
    surfaces = list()
    lines = text.split('\n')
    if len(lines) > 1:
        for i, line in enumerate(lines):
            surface = font.render(line, False, color)
            surface.convert()
        # Combine surfaces
        surface = pygame.Surface(
            (max(s.get_width() for s in surfaces),
             sum(s.get_height() for s in surfaces)))
        y = 0
        for s in surfaces:
            surface.blit(s, s.get_rect(topleft=(0, y)))
            y += s.get_height()
    else:
        surface = font.render(text, False, color)
    return surface


def draw_text(screen, text, color, font, **rect_args):
    surface = text_to_surface(text, color, font)
    surface.convert()
    rect = surface.get_rect(**rect_args)
    screen.blit(surface, rect)


def hash_surface_and_color(surface, color):
    return str(hash(surface)) + str(color)


@memoize_with(hash_surface_and_color)
def colorize_surface(surface, color):
    """
    Multiply every pixel in the surface by the given color and return the new surface
    You should probably convert_alpha() before-hand
    """
    print('Called! ' + str([surface, color]))
    new_surface = surface.copy()
    new_surface.fill(color, None, pygame.BLEND_RGBA_MULT)
    return new_surface


