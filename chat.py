from time import time

import pygame

from loader import fonts
from keys import *
import network

chatting = False


class Chat(object):
    def __init__(self):
        self.log = list()
        self.current_message = ''

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_ENTER:
                self.add(self.current_message)
                network.send_message('T{id}:{msg}'.format(id=network.character, msg=self.current_message))
                self.current_message = ''
                return True
            elif event.key == K_ESC:
                self.current_message = ''
                return True
            elif event.key == K_BACKSPACE:
                self.current_message = self.current_message[:-1]
            elif event.unicode:
                self.current_message += event.unicode
        return False

    def add(self, msg, timestamp=None):
        timestamp = timestamp or time()
        self.log.append((timestamp, msg))

    def draw(self, screen):
        stay_time = 15.0
        fade_time = 10.0
        showing = [tup for tup in self.log if time() - tup[0] <= stay_time]
        if chatting:
            showing += [(time(), self.current_message)]
        for i, tup in enumerate(showing):
            td = time() - tup[0]
            text_surface = fonts['chat'].render(tup[1], False, (255, 255, 0))
            y = screen.get_height() - ((len(showing) - 1) - i) * 28
            rect = text_surface.get_rect(bottomleft=(0, y))
            if td > fade_time:
                text_surface.set_alpha(255 - (td - fade_time) * 255 / (stay_time - fade_time))
            screen.blit(text_surface, rect)
        if chatting:
            pygame.draw.line(screen, (255, 255, 0), (3, screen.get_height() - 34),
                             (screen.get_width() - 3, screen.get_height() - 34), 2)

chat = Chat()

