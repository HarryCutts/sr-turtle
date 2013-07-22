from __future__ import division

import pygame

from markers import WallMarker
from math import pi

MARKERS_PER_WALL = 7

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

    def __init__(self, objects=None, wall_markers=True):
        self.objects = objects if objects is not None else []
        if wall_markers:
            self._populate_wall_markers()

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
