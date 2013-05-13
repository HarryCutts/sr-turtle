#!/usr/bin/python2.7

from __future__ import division
from math import degrees

import pygame

PIXELS_PER_METER = 100

def to_pixel_coord(world_coord):
    x, y = world_coord
    x, y = (x * PIXELS_PER_METER, y * PIXELS_PER_METER)
    return (x + 320, y + 240)  # TODO: centralise these constants

class Display(object):

    def __init__(s, objects=[]):
        s.objects = objects

        pygame.init()
        s._window = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("SR Turtle Robot Simulator")
        s._screen = pygame.display.get_surface()
        s._robot_png = pygame.image.load("robot.png").convert()
        s._draw()

    def _draw(s):
        if s.objects == None or len(s.objects) == 0:
            return

        s._screen.fill((0, 0, 0))

        for o in s.objects:
            with o.lock:
                object_surface = o.get_surface()
                ow, oh = object_surface.get_size()
                x, y = to_pixel_coord(o.location)
                screen_location = (x - ow / 2., y - oh / 2.)
                s._screen.blit(object_surface, screen_location)

        pygame.display.flip()

    ## Public Methods ##

    def tick(s, time_passed):
        for o in s.objects:
            o.tick(time_passed)

        s._draw()
