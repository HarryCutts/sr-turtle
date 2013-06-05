#!/usr/bin/python2.7

from __future__ import division

import pygame, sys, os, thread
import threading
from pygame.locals import *
from math import pi, sin, cos, degrees

_robot_png = None

class Motor(object):
    _target = 0

    def __init__(s, robot):
        s._robot = robot

    @property
    def target(s):
        return s._target

    @target.setter
    def target(s, value):
        s._robot.lock.acquire()
        s._target = value
        s._robot.lock.release()

class SimRobot(object):
    _origin_offset = (320, 240)
    lock = threading.RLock()

    width = 0.48

    location = (0, 0)
    heading = 0

    motors = None

    ## Constructor ##

    def __init__(s, arena):
        s.motors = [Motor(s), Motor(s)]
        arena.objects.append(s)

    ## Internal methods ##

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
                print sa
                theta = sa * t / r
                d = (r * sin(theta)) * sin((pi - theta) / 2)
                phi = 0.5*pi - (pi - theta) / 2

        # Work out how this translates to coordinates
        dx = d * cos(phi + s.heading)
        dy = -d * sin(phi + s.heading)
        return dx, dy, theta

    ## "Public" methods ##

    def get_surface(s):
        global _robot_png
        if _robot_png == None:
            _robot_png = pygame.image.load("robot.png").convert()
        with s.lock:
            return pygame.transform.rotate(_robot_png, degrees(s.heading))

    def tick(s, time_passed):
        s.lock.acquire()
        dx, dy, dh = s._calculate_movement(time_passed)
        x, y = s.location
        s.location = (x + dx, y + dy)
        s.heading += dh
        s.lock.release()
