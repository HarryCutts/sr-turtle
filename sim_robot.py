#!/usr/bin/python2.7

from __future__ import division

import pygame, sys, os, thread
import threading
from pygame.locals import *
from math import pi, sin, cos, degrees, hypot

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
    lock = threading.RLock()

    width = 0.48

    location = (0, 0)
    heading = 0

    motors = None

    ## Constructor ##

    def __init__(s, arena):
        s.arena = arena
        s.motors = [Motor(s), Motor(s)]
        arena.objects.append(s)

    ## Internal methods ##

    def _calculate_corners(s, location=location, heading=heading):
        corners = []
        r = hypot(s.width / 2, s.width / 2)
        x, y = location
        angle = pi / 4
        while angle < 2 * pi:
            corners.append((x + r * cos(heading + angle), y + r * sin(heading + angle)))
            angle += pi / 2

        return corners

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

    def move_and_rotate(s, dx, dy, dh):
        # TODO: Move right up to the arena edge when colliding
        x, y = s.location
        new_location = (x + dx, y + dy)
        new_heading = s.heading + dh
        new_corners = s._calculate_corners(new_location, new_heading)
        can_move = [True, True]
        friction_factor = 1
        for c in new_corners:
            inside, dimension = s.arena.contains_point(c)
            if not inside:
                can_move[dimension] = False
                # Reduce overall movement to account for friction
                friction_factor = friction_factor * 0.3

        # TODO: Turn towards the wall when pushing against it

        s.location = (x + (dx * friction_factor) if can_move[0] else x, \
                      y + (dy * friction_factor) if can_move[1] else y)

        s.heading = new_heading
        return can_move[0] and can_move[1]

    def tick(s, time_passed):
        s.lock.acquire()
        dx, dy, dh = s._calculate_movement(time_passed)
        s.move_and_rotate(dx, dy, dh)
        s.lock.release()
