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
    def left(s):   return -s.size[0] / 2
    @property
    def right(s):  return s.size[0] / 2
    @property
    def top(s):    return -s.size[1] / 2
    @property
    def bottom(s): return s.size[1] / 2

    def __init__(s, objects=[], wall_markers=True):
        s.objects = objects
        if wall_markers:
            x_interval = s.size[0] / (MARKERS_PER_WALL + 1)
            y_interval = s.size[1] / (MARKERS_PER_WALL + 1)
            # Left wall
            y = s.top + y_interval
            for i in range(0, MARKERS_PER_WALL):
                s.objects.append(WallMarker(s, i, (s.left, y), 0))
                y += y_interval

            # Bottom wall
            x = s.left + x_interval
            for i in range(MARKERS_PER_WALL, 2*MARKERS_PER_WALL):
                s.objects.append(WallMarker(s, i, (x, s.bottom), pi / 2))
                x += x_interval

            # Right wall
            y = s.bottom - y_interval
            for i in range(2*MARKERS_PER_WALL, 3*MARKERS_PER_WALL):
                s.objects.append(WallMarker(s, i, (s.right, y), pi))
                y -= y_interval

            # Top wall
            x = s.right - x_interval
            for i in range(3*MARKERS_PER_WALL, 4*MARKERS_PER_WALL):
                s.objects.append(WallMarker(s, i, (x, s.top), 3 * pi / 2))
                x -= x_interval

    ## Public Methods ##

    def contains_point(s, point):
        x, y = point
        if not (s.left < x < s.right):
            return False, 0, max(s.left, min(x, s.right))
        elif not (s.top < y < s.bottom):
            return False, 1, max(s.top, min(y, s.bottom))
        else:
            return True, None, None

    def tick(s, time_passed):
        for o in s.objects:
            if hasattr(o, "tick"):
                o.tick(time_passed)
