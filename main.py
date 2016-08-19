#!/usr/bin/env python
import asyncore
import logging
import random
import sys
import time

import pygame

from world import World
from gameobject import GameObject, Static
from physics import V
from witch import Witch
from ww import WW
from cat import Cat
from spider import Spider
from loader import load_all, images, fonts
from keys import *
from network import Server, ChatHandler, clients
import network
import chat
from map import load_world


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Initializing pygame')
    pygame.init()

    size = w, h = 640, 480
    fps = 30
    logging.info('Setting screen mode')
    screen = pygame.display.set_mode((w, h))
    load_all()

    # Character select
    while network.character is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key not in pressed_keys:
                    pressed_keys.add(event.key)
                    if event.key == K_C:
                        network.character = 'c'
                    elif event.key == K_W:
                        network.character = 'w'
                    elif event.key == K_E:
                        network.character = 'e'
                    elif event.key == K_ESC:
                        sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)

        text = 'Press W for Werewolf\nPress E for Evil Witch\nPress C for Cat'
        lines = text.split('\n')
        for i, line in enumerate(lines):
            text_surface = fonts['select'].render(line, False, (255, 255, 0))
            yo = (i - ((len(lines) - 1) / 2.0)) * 48
            rect = text_surface.get_rect(center=(w / 2, h / 2 + yo))
            text_surface.convert()
            screen.blit(text_surface, rect)
        pygame.display.flip()

        time.sleep(0.03)

    world = World(w, h)
    objs, start_pos = load_world('maps/test.txt')
    for obj in objs:
        world.add_object(obj)
    if network.character == 'w':
        world.add_object(WW(pos=start_pos, authority=True))
    if network.character == 'e':
        world.add_object(Witch(pos=start_pos, authority=True))
    if network.character == 'c':
        world.add_object(Cat(pos=start_pos, authority=True))

    last_update = time.time()

    while True:
        start_time = time.time()

        # Handle events
        logging.debug('Handle events')
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key not in pressed_keys:
                    if chat.chatting:
                        if chat.chat.handle(event):
                            chat.chatting = False
                    else:
                        pressed_keys.add(event.key)
                        if event.key == K_C:
                            to_remove = list()
                            for obj in world.objs.values():
                                if isinstance(obj, Spider):
                                    to_remove.append(obj)
                                if isinstance(obj, Static):
                                    to_remove.append(obj)
                            for obj in to_remove:
                                world.remove_object(obj)
                            network.client = ChatHandler(world=world)
                            network.client.send_all()
                        elif event.key == K_S:
                            network.server = Server(world)
                        elif event.key == K_ENTER:
                            chat.chatting = True
                            pressed_keys.clear()
                        elif event.key == K_ESC:
                            sys.exit()
                        elif event.key == K_BACKSPACE:  # lol
                            wall = GameObject(sprites=images['bush'], wall=True, pos=world.players[0].pos)
                            world.add_object(wall)
            elif event.type == pygame.KEYUP:
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)

            if not chat.chatting:
                world.handle(event)

        # Handle game logic
        logging.debug('Game Logic')
        dt = time.time() - last_update
        last_update = time.time()
        world.run(dt)
        world.post_run()
        world.validate()

        # Draw
        logging.debug('Draw')
        screen.fill((0, 0, 0))
        world.draw(screen)
        chat.chat.draw(screen)
        pygame.display.flip()

        logging.debug('Handle Network')
        # Send/receive network messages
        if network.client:
            asyncore.loop(timeout=0, count=20)
        if network.server:
            asyncore.loop(map=clients, timeout=0, count=20)

        # Sleep enough time to get 30 fps
        sleep_for = max(0, 1./fps - (time.time() - start_time))
        logging.debug('Sleep for {0}'.format(sleep_for))
        time.sleep(sleep_for)


if __name__ == '__main__':
    import cProfile
    stats = cProfile.run('main()', sort=1)
    # stats.sort_stats('calls')
    # stats.print_stats()
