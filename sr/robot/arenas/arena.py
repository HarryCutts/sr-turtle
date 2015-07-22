from __future__ import division

from math import pi
from random import random

from ..display import get_surface, PIXELS_PER_METER
from ..markers import WallMarker, Token

import threading

import pypybox2d

MARKERS_PER_WALL = 7

ARENA_FLOOR_COLOR = (0x11, 0x18, 0x33)
ARENA_MARKINGS_COLOR = (0xD0, 0xD0, 0xD0)
ARENA_MARKINGS_WIDTH = 2

def lerp(delta, a, b):
    return delta*b + (1-delta)*a

class Arena(object):
    size = (8, 8)
    start_locations = [(0, 0)]
    start_headings = [0]

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
                            count = MARKERS_PER_WALL, start = 3*MARKERS_PER_WALL, angle = 0)
        # Right wall
        self._populate_wall(left = (self.right, self.top), right = (self.right, self.bottom),
                            count = MARKERS_PER_WALL, start = MARKERS_PER_WALL, angle = pi)
        # Bottom wall
        self._populate_wall(left = (self.right, self.bottom), right = (self.left, self.bottom),
                            count = MARKERS_PER_WALL, start = 2*MARKERS_PER_WALL, angle = pi / 2)
        # Top wall
        self._populate_wall(left = (self.left, self.top), right = (self.right, self.top),
                            count = MARKERS_PER_WALL, start = 0, angle = 3*pi / 2)

    def _init_physics(self):
        self._physics_world = pypybox2d.world.World(gravity=(0, 0))
        # Global lock for simulation
        self.physics_lock = threading.RLock()
        # Create the arena wall
        WALL_WIDTH = 2
        WALL_SETTINGS = {'restitution': 0.2, 'friction': 0.3}

        wall_right = self._physics_world.create_body(position=(self.right, 0),
                                                     type=pypybox2d.body.Body.STATIC)
        wall_right.create_polygon_fixture([(WALL_WIDTH, self.top - WALL_WIDTH),
                                           (WALL_WIDTH, self.bottom + WALL_WIDTH),
                                           (0, self.bottom + WALL_WIDTH),
                                           (0, self.top - WALL_WIDTH)],
                                          **WALL_SETTINGS)

        wall_left = self._physics_world.create_body(position=(self.left, 0),
                                                    type=pypybox2d.body.Body.STATIC)
        wall_left.create_polygon_fixture([(-WALL_WIDTH, self.top - WALL_WIDTH),
                                          (0, self.top - WALL_WIDTH),
                                          (0, self.bottom + WALL_WIDTH),
                                          (-WALL_WIDTH, self.bottom + WALL_WIDTH)],
                                         **WALL_SETTINGS)

        wall_top = self._physics_world.create_body(position=(0, self.top),
                                                   type=pypybox2d.body.Body.STATIC)
        wall_top.create_polygon_fixture([(self.left, 0),
                                         (self.left, -WALL_WIDTH),
                                         (self.right, -WALL_WIDTH),
                                         (self.right, 0)],
                                        **WALL_SETTINGS)

        wall_bottom = self._physics_world.create_body(position=(0, self.bottom),
                                                   type=pypybox2d.body.Body.STATIC)
        wall_bottom.create_polygon_fixture([(self.left, 0),
                                            (self.right, 0),
                                            (self.right, WALL_WIDTH),
                                            (self.left, WALL_WIDTH)],
                                           **WALL_SETTINGS)

    def __init__(self, objects=None, wall_markers=True):
        self._init_physics()
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
        with self.physics_lock:
            self._physics_world.step(time_passed,
                                     vel_iters=8,
                                     pos_iters=3)
        for obj in self.objects:
            if hasattr(obj, "tick"):
                obj.tick(time_passed)

    def draw_background(self, surface, display):
        surface.fill(ARENA_FLOOR_COLOR)

        # Motif
        motif = get_surface(self.motif_name)
        x, y = display.to_pixel_coord((0, 0), self)
        w, h = motif.get_size()
        surface.blit(motif, (x - w / 2, y - h / 2))
