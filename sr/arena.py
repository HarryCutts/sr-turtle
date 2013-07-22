from __future__ import division

import pygame

from markers import WallMarker
from math import pi

MARKERS_PER_WALL = 7

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

    def __init__(self, objects=None, wall_markers=True):
        self.objects = objects if objects is not None else []
        if wall_markers:
            x_interval = self.size[0] / (MARKERS_PER_WALL + 1)
            y_interval = self.size[1] / (MARKERS_PER_WALL + 1)
            # Left wall
            y = self.top + y_interval
            for i in range(0, MARKERS_PER_WALL):
                self.objects.append(WallMarker(self, i, (self.left, y), 0))
                y += y_interval

            # Bottom wall
            x = self.left + x_interval
            for i in range(MARKERS_PER_WALL, 2*MARKERS_PER_WALL):
                self.objects.append(WallMarker(self, i, (x, self.bottom), pi / 2))
                x += x_interval

            # Right wall
            y = self.bottom - y_interval
            for i in range(2*MARKERS_PER_WALL, 3*MARKERS_PER_WALL):
                self.objects.append(WallMarker(self, i, (self.right, y), pi))
                y -= y_interval

            # Top wall
            x = self.right - x_interval
            for i in range(3*MARKERS_PER_WALL, 4*MARKERS_PER_WALL):
                self.objects.append(WallMarker(self, i, (x, self.top), 3 * pi / 2))
                x -= x_interval

    ## Public Methods ##

    def contains_point(self, point):
        x, y = point
        if not (self.left < x < self.right):
            return False, 0, max(self.left, min(x, self.right))
        elif not (self.top < y < self.bottom):
            return False, 1, max(self.top, min(y, self.bottom))
        else:
            return True, None, None

    def tick(self, time_passed):
        for o in self.objects:
            if hasattr(o, "tick"):
                o.tick(time_passed)
