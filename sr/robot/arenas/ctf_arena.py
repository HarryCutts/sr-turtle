from __future__ import division

import pygame
from random import random
from math import pi

from arena import Arena, ARENA_MARKINGS_COLOR, ARENA_MARKINGS_WIDTH
from ..markers import Token
from ..game_object import GameObject

import pypybox2d

class CTFWall(GameObject):
    @property
    def location(self):
        return self._body.position

    @location.setter
    def location(self, new_pos):
        if self._body is None:
            return # Slight hack: deal with the initial setting from the constructor
        self._body.position = new_pos

    @property
    def heading(self):
        return self._body.angle

    @heading.setter
    def heading(self, _new_heading):
        if self._body is None:
            return # Slight hack: deal with the initial setting from the constructor
        self._body.angle = _new_heading

    def __init__(self, arena):
        self._body = arena._physics_world.create_body(position=(0, 0),
                                                      angle=0,
                                                      type=pypybox2d.body.Body.STATIC)
        self._body.create_polygon_fixture([(-0.75, -0.15),
                                           ( 0.75, -0.15),
                                           ( 0.75,  0.15),
                                           (-0.75,  0.15)],
                                          restitution=0.2,
                                          friction=0.3)
        super(CTFWall, self).__init__(arena)

    surface_name = 'sr/wall.png'

class CTFArena(Arena):
    start_locations = [(-3.6, -3.6),
                       ( 3.6, -3.6),
                       ( 3.6,  3.6),
                       (-3.6,  3.6)]

    start_headings = [0.25*pi,
                      0.75*pi,
                      -0.75*pi,
                      -0.25*pi]

    def __init__(self, objects=None, wall_markers=True, zone_flags=True):
        super(CTFArena, self).__init__(objects, wall_markers)
        self._init_walls()
        self._init_tokens(zone_flags)

    def _init_tokens(self, zone_flags):
        if zone_flags:
            token_locations = [(-3.2, -3.2),
                               ( 3.2, -3.2),
                               ( 3.2,  3.2),
                               (-3.2,  3.2),
                               (   0,    0)]
        else:
            token_locations = [(0, 0)]

        for i, location in enumerate(token_locations):
            token = Token(self, i, damping=0.5)
            token.location = location
            token.heading = pi/4
            self.objects.append(token)

    def _init_walls(self):
        wall_settings = [(-2.25, 0, 0),
                         (2.25, 0, 0),
                         (0, 2.25, pi/2),
                         (0, -2.25, pi/2)]
        for x, y, rotation in wall_settings:
            wall = CTFWall(self)
            wall.location = (x, y)
            wall.heading = rotation
            self.objects.append(wall)

    def draw_background(self, surface, display):
        super(CTFArena, self).draw_background(surface, display)

        def line(start, end):
            pygame.draw.line(surface, ARENA_MARKINGS_COLOR,
                             display.to_pixel_coord(start), display.to_pixel_coord(end),
                             ARENA_MARKINGS_WIDTH)

        def line_symmetric(start, end):
            start_x, start_y = start
            end_x, end_y = end
            line((start_x, start_y), (end_x, end_y))
            line((-start_x, start_y), (-end_x, end_y))
            line((-start_x, -start_y), (-end_x, -end_y))
            line((start_x, -start_y), (end_x, -end_y))
            line((start_y, start_x), (end_y, end_x))
            line((-start_y, start_x), (-end_y, end_x))
            line((-start_y, -start_x), (-end_y, -end_x))
            line((start_y, -start_x), (end_y, -end_x))

        line_symmetric((2, 4), (3, 3))
        line_symmetric((3, 0.15), (4, 0.15))
        line_symmetric((1.5, 0.15), (0.825, 0.825))

