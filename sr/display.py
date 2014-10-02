from __future__ import division
from math import degrees

import pygame

PIXELS_PER_METER = 100

sprites = {}

def get_surface(name):
    if name not in sprites:
        sprites[name] = pygame.image.load(name).convert_alpha()

    return sprites[name]

class Display(object):
    def __init__(self, arena):
        self.arena = arena
        arena_w, arena_h = self.arena.size
        self.size = (arena_w * PIXELS_PER_METER, arena_h * PIXELS_PER_METER)

        pygame.display.init()
        self._window = pygame.display.set_mode(self.size)
        pygame.display.set_caption("SR Turtle Robot Simulator")
        self._screen = pygame.display.get_surface()
        self._draw_background()
        self._draw()

    def __del__(self):
        pygame.display.quit()

    def _draw_background(self):
        self._background = pygame.Surface(self.size)
        self.arena.draw_background(self._background, self)

    def _draw(self):
        self._screen.blit(self._background, (0, 0))

        for obj in self.arena.objects:
            if obj.surface_name is None:
                continue
            with obj.lock:
                heading = -degrees(obj.heading)
                x, y = self.to_pixel_coord(obj.location)
            surface = get_surface(obj.surface_name)
            surface = pygame.transform.rotate(surface, heading)
            object_width, object_height = surface.get_size()
            screen_location = (x - object_width / 2, y - object_height / 2)
            self._screen.blit(surface, screen_location)

        pygame.display.flip()

    ## Public Methods ##

    def tick(self, time_passed):
        self.arena.tick(time_passed)
        # TODO: Allow multiple displays on one arena without them all ticking it
        self._draw()

    def to_pixel_coord(self, world_coord, arena=None):
        if arena is None: arena = self.arena
        offset_x = arena.size[0] / 2
        offset_y = arena.size[1] / 2
        x, y = world_coord
        x, y = ((x + offset_x) * PIXELS_PER_METER, (y + offset_y) * PIXELS_PER_METER)
        return (x, y)

