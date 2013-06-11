#!/usr/bin/python2.7

from __future__ import division
from math import degrees

import pygame

PIXELS_PER_METER = 100

def to_pixel_coord(world_coord, arena):
    offset_x = arena.size[0] / 2
    offset_y = arena.size[1] / 2
    x, y = world_coord
    x, y = ((x + offset_x) * PIXELS_PER_METER, (y + offset_y) * PIXELS_PER_METER)
    return (x, y)

sprites = {}

def get_surface(name):
    if not name in sprites:
        sprites[name] = pygame.image.load(name).convert()

    return sprites[name]

class Display(object):

    def __init__(s, arena):
        s.arena = arena

        pygame.init()
        arena_w, arena_h = s.arena.size
        s._window = pygame.display.set_mode((arena_w * PIXELS_PER_METER, arena_h * PIXELS_PER_METER))
        pygame.display.set_caption("SR Turtle Robot Simulator")
        s._screen = pygame.display.get_surface()
        s._draw()

    def _draw(s):
        s._screen.fill((0, 0, 0))

        for o in s.arena.objects:
            with o.lock:
                surface = get_surface(o.surface_name)
                surface = pygame.transform.rotate(surface, degrees(o.heading))
                object_width, object_height = surface.get_size()
                x, y = to_pixel_coord(o.location, s.arena)
                screen_location = (x - object_width / 2., y - object_height / 2.)
                s._screen.blit(surface, screen_location)

        pygame.display.flip()

    ## Public Methods ##

    def tick(s, time_passed):
        s.arena.tick(time_passed)
        # TODO: Allow multiple displays on one arena without them all ticking it
        s._draw()
