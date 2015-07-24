from __future__ import division

import pygame
from math import pi, sin, cos
from random import random

from arena import Arena, ARENA_MARKINGS_COLOR, ARENA_MARKINGS_WIDTH
from ..vision import MARKER_ARENA, MARKER_ROBOT, MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER
from ..markers import Token

HOME_ZONE_SIZE = 3

INNER_CIRCLE_RADIUS = 0.3
OUTER_CIRCLE_RADIUS = 0.8
TOKENS_PER_CIRCLE = 6

class GoldToken(Token):
    def __init__(self, *args, **kwargs):
        super(GoldToken, self).__init__(*args, damping=10,
                token_type=MARKER_TOKEN_GOLD, **kwargs)

    surface_name_released = 'sr/token.png'
    surface_name_grabbed  = 'sr/token_gold_grabbed.png'

class SilverToken(Token):
    def __init__(self, *args, **kwargs):
        super(SilverToken, self).__init__(*args, damping=10,
                token_type=MARKER_TOKEN_SILVER, **kwargs)

    surface_name_released = 'sr/token_silver.png'
    surface_name_grabbed  = 'sr/token_silver_grabbed.png'

class TwoColoursArena(Arena):
    marker_offsets = {
        MARKER_TOKEN_GOLD: 32,
        MARKER_TOKEN_SILVER: 43,
    }

    marker_sizes = {
        MARKER_TOKEN_GOLD: 0.1 * (10.0/12),
        MARKER_TOKEN_SILVER: 0.1 * (10.0/12),
    }

    start_locations = [(-3.6, -3.6),
                       ( 3.6, -3.6),
                       ( 3.6,  3.6),
                       (-3.6,  3.6)]

    start_headings = [0.25*pi,
                      0.75*pi,
                      -0.75*pi,
                      -0.25*pi]


    def __init__(self, objects=None, wall_markers=True):
        super(TwoColoursArena, self).__init__(objects, wall_markers)

        def place_token_circle(radius, number_offset=0, angle_offset=0.5*pi):
            for i in range(TOKENS_PER_CIRCLE):
                # TODO: rotations
                token_type = GoldToken if i % 2 == 0 else SilverToken
                token = token_type(self, number_offset + i)
                angle = angle_offset + (2*pi / TOKENS_PER_CIRCLE) * i
                token.location = (cos(angle) * radius, sin(angle) * radius)
                self.objects.append(token)

        place_token_circle(INNER_CIRCLE_RADIUS)
        place_token_circle(OUTER_CIRCLE_RADIUS, number_offset=TOKENS_PER_CIRCLE,
                angle_offset=1.5*pi)

    def draw_background(self, surface, display):
        super(TwoColoursArena, self).draw_background(surface, display)

        def line(start, end):
            pygame.draw.line(surface, ARENA_MARKINGS_COLOR, \
                             start, end, ARENA_MARKINGS_WIDTH)

        # Home zones
        def draw_corner_box(corner, width, depth):
            x, y = corner
            wall_corner_1  = display.to_pixel_coord((x + width, y))
            wall_corner_2  = display.to_pixel_coord((x, y + depth))
            outside_corner = display.to_pixel_coord((x + width, y + depth))
            line(wall_corner_1, outside_corner)
            line(outside_corner, wall_corner_2)

        draw_corner_box((self.left,  self.top),     HOME_ZONE_SIZE, HOME_ZONE_SIZE)
        draw_corner_box((self.right, self.top),    -HOME_ZONE_SIZE, HOME_ZONE_SIZE)
        draw_corner_box((self.right, self.bottom), -HOME_ZONE_SIZE, -HOME_ZONE_SIZE)
        draw_corner_box((self.left,  self.bottom),  HOME_ZONE_SIZE, -HOME_ZONE_SIZE)
