from __future__ import division

import pygame
from math import pi
from random import random

from arena import Arena, ARENA_MARKINGS_COLOR, ARENA_MARKINGS_WIDTH
from ..markers import Token

class PiratePlunderArena(Arena):
    start_locations = [( 0, -3),
                       ( 3,  0),
                       ( 0,  3),
                       (-3,  0)]

    start_headings = [0.5*pi,
                      pi,
                      -0.5*pi,
                      0]

    def __init__(self, objects=None, wall_markers=True, num_tokens=5):
        super(PiratePlunderArena, self).__init__(objects, wall_markers)

        for i in range(num_tokens):
            token = Token(self, i, damping=10)
            token.location = (random() * 4 - 2, random() * 4 - 2)
            self.objects.append(token)

    def draw_background(self, surface, display):
        super(PiratePlunderArena, self).draw_background(surface, display)

        # Corners of the inside square
        top_left     = display.to_pixel_coord((self.left + self.zone_size, self.top + self.zone_size), self)
        top_right    = display.to_pixel_coord((self.right - self.zone_size, self.top + self.zone_size), self)
        bottom_right = display.to_pixel_coord((self.right - self.zone_size, self.bottom - self.zone_size), self)
        bottom_left  = display.to_pixel_coord((self.left + self.zone_size, self.bottom - self.zone_size), self)

        # Lines separating zones
        def line(start, end):
            pygame.draw.line(surface, ARENA_MARKINGS_COLOR, \
                             start, end, ARENA_MARKINGS_WIDTH)

        line((0, 0), top_left)
        line((display.size[0], 0), top_right)
        line(display.size, bottom_right)
        line((0, display.size[1]), bottom_left)

        # Square separating zones from centre
        pygame.draw.polygon(surface, ARENA_MARKINGS_COLOR, \
                            [top_left, top_right, bottom_right, bottom_left], 2)
