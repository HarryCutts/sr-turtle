from __future__ import division

import threading, time, pygame

from arenas import PiratePlunderArena, CTFArena
from display import Display

DEFAULT_GAME = 'pirate-plunder'

GAMES = {'pirate-plunder': PiratePlunderArena,
         'ctf': CTFArena}

class Simulator(object):
    def __init__(self, config={}, size=(8, 8), frames_per_second=30):
        try:
            game_name = config['game']
            del config['game']
        except KeyError:
            game_name = DEFAULT_GAME
        game = GAMES[game_name]
        self.arena = game(**config)

        self.display = Display(self.arena)

        self._loop_thread = threading.Thread(target=self._main_loop, args=(frames_per_second,))
        self._loop_thread.setDaemon(True)
        self._loop_thread.start()

    def _main_loop(self, frames_per_second):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            self.display.tick(1/frames_per_second)
            clock.tick(frames_per_second)

    def __del__(self):
        pygame.quit()
