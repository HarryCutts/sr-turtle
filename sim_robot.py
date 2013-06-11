#!/usr/bin/python2.7

from __future__ import division

import pygame, sys, os, thread
import threading
from pygame.locals import *
from math import pi, sin, cos, degrees, hypot

class Motor(object):
    _target = 0

    def __init__(s, robot):
        s._robot = robot

    @property
    def target(s):  return s._target

    @target.setter
    def target(s, value):
        with s._robot.lock:
            s._target = value

class SimRobot(object):
    width = 0.48

    location = (0, 0)
    heading = 0

    lock = threading.RLock()
    surface_name = 'robot.png'

    arena = None
    motors = None

    ## Constructor ##

    def __init__(s, arena):
        s.arena = arena
        s.motors = [Motor(s), Motor(s)]
        s.corners = s._calculate_corners()
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

    def move_and_rotate(s, move_by, dh):
        # TODO: Move right up to the arena edge when colliding
        x, y = s.location
        new_heading = s.heading + dh
        new_location = (x + move_by[0], y + move_by[1])
        new_corners = s._calculate_corners(new_location, new_heading)
        can_move = [True, True]
        can_rotate = True
        friction_factor = 1
        for i in range(len(new_corners)):
            c = new_corners[i]
            inside, dim, furthest = s.arena.contains_point(c)
            if not inside:
                can_rotate = False  # a passable approximation

                # Work out where the collision actually happens, and move to that point
                new_d = furthest - s.corners[i][dim]
                if move_by[dim] > 0 and new_d > 0 or move_by[dim] < 0 and new_d < 0:
                    # Shorten the vector so that it just touches the wall
                    fraction = new_d / move_by[dim]
                    move_by = (new_d, move_by[1] * fraction) if dim == 0 else \
                              (move_by[0] * fraction, new_d)

                    # Recalculate the corner locations for the new vector
                    new_location = (x + move_by[0], y + move_by[1])
                    new_corners = s._calculate_corners(new_location, new_heading)
                else:
                    # Robot already touching the wall, so slide along it
                    can_move[dim] = False
                    friction_factor *= 0.3

        # TODO: Turn towards the wall when pushing against it

        s.location = (x + (move_by[0] * friction_factor) if can_move[0] else x, \
                      y + (move_by[1] * friction_factor) if can_move[1] else y)

        if can_rotate:
            s.heading = new_heading

        if can_rotate or can_move[0] or can_move[1]:
            s.corners = new_corners

    def tick(s, time_passed):
        with s.lock:
            dx, dy, dh = s._calculate_movement(time_passed)
            s.move_and_rotate((dx, dy), dh)
