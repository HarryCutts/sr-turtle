from __future__ import division

import threading, time, pygame

from arenas import PiratePlunderArena, CTFArena, TwoColoursArena
from display import Display
from vision import init_marker_info

DEFAULT_GAME = 'pirate-plunder'

GAMES = {'pirate-plunder': PiratePlunderArena,
         'ctf': CTFArena,
         'two-colours': TwoColoursArena}

class Simulator(object):
    def __init__(self, config={}, size=(8, 8), frames_per_second=30, foreground=False):
        try:
            game_name = config['game']
            del config['game']
        except KeyError:
            game_name = DEFAULT_GAME
        game = GAMES[game_name]
        init_marker_info(game)
        self.arena = game(**config)

        self.display = Display(self.arena)

        self.foreground = foreground
        self.frames_per_second = frames_per_second

        if not self.foreground:
            self._loop_thread = threading.Thread(target=self._main_loop, args=(frames_per_second,))
            self._loop_thread.setDaemon(True)
            self._loop_thread.start()

    def run(self):
        if not self.foreground:
            raise RuntimeError('Simulator runs in the background. Try passing foreground=True')
        self._main_loop(self.frames_per_second)

    def _main_loop(self, frames_per_second):
        clock = pygame.time.Clock()

        while True:
            if any(event.type == pygame.QUIT
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
                    for event in pygame.event.get()):
                break

            self.display.tick(1/frames_per_second)
            clock.tick(frames_per_second)

        pygame.quit()
