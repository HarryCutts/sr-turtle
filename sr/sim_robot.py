#!/usr/bin/python2.7

from __future__ import division

import pygame, time, exceptions
from pygame.locals import *
from math import pi, sin, cos, degrees, hypot, atan2

from game_object import GameObject
from vision import Marker, Point, PolarCoord

SPEED_SCALE_FACTOR = 0.02
MAX_MOTOR_SPEED = 100

GRAB_RADIUS = 0.4
HALF_GRAB_SECTOR_WIDTH = pi / 4
HALF_FOV_WIDTH = pi / 6

GRABBER_OFFSET = 0.25

class AlreadyHoldingSomethingException(exceptions.Exception):
    def __str__(s):
        return "The robot is already holding something."

class Motor(object):
    _target = 0

    def __init__(s, robot):
        s._robot = robot

    @property
    def target(s):  return s._target

    @target.setter
    def target(s, value):
        value = min(max(value, -MAX_MOTOR_SPEED), MAX_MOTOR_SPEED)
        with s._robot.lock:
            s._target = value

class SimRobot(GameObject):
    width = 0.48

    surface_name = 'robot.png'

    motors = None

    _holding = None

    ## Constructor ##

    def __init__(s, simulator):
        GameObject.__init__(s, simulator.arena)
        s.motors = [Motor(s), Motor(s)]
        s.corners = s._calculate_corners()
        simulator.arena.objects.append(s)

    ## Internal methods ##

    def _calculate_corners(s, location=None, heading=None):
        if location == None: location = s.location
        if heading == None:  heading = s.heading

        corners = []
        r = hypot(s.width / 2, s.width / 2)
        x, y = location
        angle = pi / 4
        while angle < 2 * pi:
            corners.append((x + r * cos(heading + angle), y + r * sin(heading + angle)))
            angle += pi / 2

        return corners

    def _calculate_movement(s, t):
        sl, sr = s.motors[0].target * SPEED_SCALE_FACTOR, s.motors[1].target * SPEED_SCALE_FACTOR
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
        dx = d * cos(phi - s.heading)
        dy = -d * sin(phi - s.heading)
        return dx, dy, -theta

    def _move_and_rotate(s, move_by, dh):
        x, y = s.location
        new_heading = s.heading + dh
        if new_heading > pi:
            new_heading -= 2 * pi
        elif new_heading < -pi:
            new_heading += 2 * pi
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
            if s._holding != None:
                s._holding.location = (x + cos(s.heading) * GRABBER_OFFSET, \
                                       y + sin(s.heading) * GRABBER_OFFSET)

    ## "Public" methods for simulator code ##

    def tick(s, time_passed):
        with s.lock:
            dx, dy, dh = s._calculate_movement(time_passed)
            s._move_and_rotate((dx, dy), dh)

    ## "Public" methods for user code ##

    def grab(s):
        if s._holding != None:
            raise AlreadyHoldingSomethingException()

        with s.lock:
            x, y = s.location
            heading = s.heading

        def object_filter(o):
            rel_x, rel_y = (o.location[0] - x, o.location[1] - y)
            direction = atan2(rel_y, rel_x)
            return o.grabbable and hypot(rel_x, rel_y) <= GRAB_RADIUS and \
                   -HALF_GRAB_SECTOR_WIDTH < direction - heading < HALF_GRAB_SECTOR_WIDTH

        objects = filter(object_filter, s.arena.objects)
        if len(objects) > 0:
            s._holding = objects[0]
            s._holding.grab()
            s._holding.location = (x + cos(heading) * GRABBER_OFFSET, \
                                   y + sin(heading) * GRABBER_OFFSET)
            return True
        else:
            return False

    def release(s):
        if s._holding != None:
            s._holding.release()
            s._holding = None
            return True
        else:
            return False

    def see(s, res=(800,600)):
        with s.lock:
            x, y = s.location
            heading = s.heading

        acq_time = time.time()

        def object_filter(o):
            # Choose only marked objects within the field of view
            direction = atan2(o.location[1] - y, o.location[0] - x)
            return o.marker_info != None \
                   and -HALF_FOV_WIDTH < direction - heading < HALF_FOV_WIDTH

        def marker_map(o):
            # Turn a marked object into a Marker
            rel_x, rel_y = (o.location[0] - x, o.location[1] - y)
            polar_coord = PolarCoord(length=hypot(rel_x, rel_y), \
                                     rot_y=degrees(atan2(rel_y, rel_x) - heading))
            # TODO: Check polar coordinates are the right way around
            return Marker(info=o.marker_info,
                          centre=Point(polar_coord),
                          res=res,
                          timestamp=acq_time)

        return map(marker_map, filter(object_filter, s.arena.objects))
