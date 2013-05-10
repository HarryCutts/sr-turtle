#!/usr/bin/python2.7

import pygame, sys, os, thread
import threading
from pygame.locals import *
from math import sin, cos, degrees

from ticker import *

PIXELS_PER_METER = 100

class Motor(object):
    _target = 0

    def __init__(s, robot):
        s._robot = robot

    @property
    def target(s):
        return s._target

    @target.setter
    def target(s, value):
        s._robot._lock.acquire()
        s._target = value
        s._robot._lock.release()

class SimRobot(object):
    _origin_offset = (320, 240)
    _lock = threading.Lock()

    width = 0.48

    location = (0, 0)
    heading = 0

    motors = None

    ## Constructor ##

    def __init__(s):
        s.motors = [Motor(s), Motor(s)]
        # Display code
        pygame.init()
        s._window = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("SR Robot Simulator")
        s._screen = pygame.display.get_surface()
        s._robot_png = pygame.image.load("robot.png").convert()
        s._draw()

    ## Internal methods ##

    def _to_pixel_coord(s, world_coord):
        x, y = world_coord
        x, y = (x * PIXELS_PER_METER, y * PIXELS_PER_METER)
        return (x + s._origin_offset[0], y + s._origin_offset[1])

    def _draw(s):
        robot_surface = pygame.transform.rotate(s._robot_png, \
                degrees(s.heading))
        rw, rh = robot_surface.get_size()
        x, y = s._to_pixel_coord(s.location)
        screen_location = (x - rw / 2., y - rh / 2.)
        s._screen.fill((0, 0, 0))
        s._screen.blit(robot_surface, screen_location)
        pygame.display.flip()

    def _calculate_movement(s, t):
        sl, sr = s.motors[0].target, s.motors[1].target
        w = s.width

        # To be calculated
        d = None
        theta = None
        phi = None

        if sl == sr:
            # going straight forwards
            d, phi = (sl * t, 0)
            theta = 0
        else:
            r = (sl * w) / (sr - sl) + 0.5 * w
            if r == 0:
                # Turning on the spot
                d, phi = (0, 0)
                theta = (sr * t) / (0.5 * w)
            else:
                sa = (sl + sr) / 2
                theta = sa * t / r
                d = (r * sin(theta)) * sin((180 - theta) / 2)
                phi = 90 - (180 - theta) / 2

        # Work out how this translates to coordinates
        dx = d * cos(phi + s.heading)
        dy = -d * sin(phi + s.heading)
        return dx, dy, theta

    ## "Public" methods ##

    def start(s):
        thread.start_new(ticker, (0.015, s))

    def tick(s, time_passed):
        s._lock.acquire()
        dx, dy, dh = s._calculate_movement(time_passed)
        x, y = s.location
        s.location = (x + dx, y + dy)
        s.heading += dh
        s._draw()
        s._lock.release()
