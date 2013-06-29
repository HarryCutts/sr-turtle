from __future__ import division

import threading, time, pygame
from random import random

from arena import Arena
from display import Display
from markers import Token

class Simulator(object):
    def __init__(s, num_tokens=5, size=(8, 8), frames_per_second=30):
        s.arena = Arena()

        for i in range(num_tokens):
            token = Token(s.arena, i)
            token.location = (random() * 4 - 2, random() * 4 - 2)
            s.arena.objects.append(token)

        s.display = Display(s.arena)

        s._loop_thread = threading.Thread(target=s._main_loop, args=(frames_per_second,))
        s._loop_thread.start()

    def _main_loop(s, frames_per_second):
        clock = pygame.time.Clock()

        done = False

        while done == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            s.display.tick(1/frames_per_second)
            clock.tick(frames_per_second)

    def __del__(s):
        pygame.quit()
