from __future__ import division

import pygame
from math import pi
from random import random

from display import get_surface, PIXELS_PER_METER
from markers import WallMarker, Token

MARKERS_PER_WALL = 7

ARENA_FLOOR_COLOR = (0x11, 0x18, 0x33)
ARENA_MARKINGS_COLOR = (0xD0, 0xD0, 0xD0)
ARENA_MARKINGS_WIDTH = 2

def lerp(delta, a, b):
    return delta*b + (1-delta)*a

class Arena(object):
    size = (6, 6)

    zone_size = 1

    motif_name = 'sr/sr_round_flat.png'

    @property
    def left(self):
        return -self.size[0] / 2
    @property
    def right(self):
        return self.size[0] / 2
    @property
    def top(self):
        return -self.size[1] / 2
    @property
    def bottom(self):
        return self.size[1] / 2

    def _populate_wall(self, left, right, count, start, angle):
        left_bound_x, left_bound_y = left
        right_bound_x, right_bound_y = right
        for i in xrange(count):
            delta = (i + 1) / (count + 1)
            x = lerp(delta, left_bound_x, right_bound_x)
            y = lerp(delta, left_bound_y, right_bound_y)
            identifier = start + i
            self.objects.append(WallMarker(self, identifier, (x, y), angle))

    def _populate_wall_markers(self):
        # Left wall
        self._populate_wall(left = (self.left, self.bottom), right = (self.left, self.top),
                            count = MARKERS_PER_WALL, start = 0, angle = 0)
        # Right wall
        self._populate_wall(left = (self.right, self.bottom), right = (self.right, self.top),
                            count = MARKERS_PER_WALL, start = MARKERS_PER_WALL, angle = pi)
        # Bottom wall
        self._populate_wall(left = (self.left, self.bottom), right = (self.right, self.bottom),
                            count = MARKERS_PER_WALL, start = 2*MARKERS_PER_WALL, angle = pi / 2)
        # Top wall
        self._populate_wall(left = (self.left, self.top), right = (self.right, self.top),
                            count = MARKERS_PER_WALL, start = 3*MARKERS_PER_WALL, angle = 3*pi / 2)

    def __init__(self, objects=None, wall_markers=True, num_tokens=5):
        self.objects = objects if objects is not None else []
        if wall_markers:
            self._populate_wall_markers()

        for i in range(num_tokens):
            token = Token(self, i)
            token.location = (random() * 4 - 2, random() * 4 - 2)
            self.objects.append(token)

    ## Public Methods ##

    def contains_point(self, (x, y)):
        if not (self.left < x < self.right):
            return False, 0, max(self.left, min(x, self.right))
        elif not (self.top < y < self.bottom):
            return False, 1, max(self.top, min(y, self.bottom))
        else:
            return True, None, None

    def tick(self, time_passed):
        for obj in self.objects:
            if hasattr(obj, "tick"):
                obj.tick(time_passed)

    def draw_background(self, surface, display):
        surface.fill(ARENA_FLOOR_COLOR)

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

        # Motif
        motif = get_surface(self.motif_name)
        x, y = display.to_pixel_coord((0, 0), self)
        w, h = motif.get_size()
        surface.blit(motif, (x - w / 2, y - h / 2))
