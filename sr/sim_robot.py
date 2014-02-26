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
    def __str__(self):
        return "The robot is already holding something."

class MotorChannel(object):
    def __init__(self, robot):
        self._power = 0
        self._robot = robot

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        value = min(max(value, -MAX_MOTOR_SPEED), MAX_MOTOR_SPEED)
        with self._robot.lock:
            self._power = value

class Motor:
    """Represents a motor board."""
    # This is named `Motor` instead of `MotorBoard` for consistency with pyenv

    # TODO: add a dummy serial number

    def __init__(self, robot):
        self._robot = robot

        self.m0 = MotorChannel(robot)
        self.m1 = MotorChannel(robot)

class SimRobot(GameObject):
    width = 0.48

    surface_name = 'sr/robot.png'

    _holding = None

    ## Constructor ##

    def __init__(self, simulator):
        GameObject.__init__(self, simulator.arena)
        self.motors = [Motor(self)]
        self.corners = self._calculate_corners(self.location, self.heading)
        simulator.arena.objects.append(self)

    ## Internal methods ##

    def _calculate_corners(self, location, heading):
        corners = []
        r = hypot(self.width / 2, self.width / 2)
        x, y = location
        angle = pi / 4
        while angle < 2 * pi:
            corners.append((x + r * cos(heading + angle), y + r * sin(heading + angle)))
            angle += pi / 2

        return corners

    def _calculate_movement(self, t):
        sl, sr = self.motors[0].m0.power * SPEED_SCALE_FACTOR, self.motors[0].m1.power * SPEED_SCALE_FACTOR
        w = self.width

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
        dx = d * cos(phi - self.heading)
        dy = -d * sin(phi - self.heading)
        return dx, dy, -theta

    def _move_and_rotate(self, move_by, dh):
        x, y = self.location
        new_heading = self.heading + dh
        if new_heading > pi:
            new_heading -= 2 * pi
        elif new_heading < -pi:
            new_heading += 2 * pi
        new_location = (x + move_by[0], y + move_by[1])
        new_corners = self._calculate_corners(new_location, new_heading)
        can_move = [True, True]
        can_rotate = True
        friction_factor = 1
        for i, c in enumerate(new_corners):
            inside, dim, furthest = self.arena.contains_point(c)
            if not inside:
                can_rotate = False  # a passable approximation

                # Work out where the collision actually happens, and move to that point
                new_d = furthest - self.corners[i][dim]
                if move_by[dim] > 0 and new_d > 0 or move_by[dim] < 0 and new_d < 0:
                    # Shorten the vector so that it just touches the wall
                    fraction = new_d / move_by[dim]
                    move_by = (new_d, move_by[1] * fraction) if dim == 0 else \
                              (move_by[0] * fraction, new_d)

                    # Recalculate the corner locations for the new vector
                    new_location = (x + move_by[0], y + move_by[1])
                    new_corners = self._calculate_corners(new_location, new_heading)
                else:
                    # Robot already touching the wall, so slide along it
                    can_move[dim] = False
                    friction_factor *= 0.3

        # TODO: Turn towards the wall when pushing against it

        self.location = (x + (move_by[0] * friction_factor) if can_move[0] else x, \
                         y + (move_by[1] * friction_factor) if can_move[1] else y)

        if can_rotate:
            self.heading = new_heading

        if can_rotate or can_move[0] or can_move[1]:
            self.corners = new_corners
            if self._holding != None:
                self._holding.location = (x + cos(self.heading) * GRABBER_OFFSET, \
                                          y + sin(self.heading) * GRABBER_OFFSET)

    ## "Public" methods for simulator code ##

    def tick(self, time_passed):
        with self.lock:
            dx, dy, dh = self._calculate_movement(time_passed)
            self._move_and_rotate((dx, dy), dh)

    ## "Public" methods for user code ##

    def grab(self):
        if self._holding is not None:
            raise AlreadyHoldingSomethingException()

        with self.lock:
            x, y = self.location
            heading = self.heading

        def object_filter(o):
            rel_x, rel_y = (o.location[0] - x, o.location[1] - y)
            direction = atan2(rel_y, rel_x)
            return o.grabbable and hypot(rel_x, rel_y) <= GRAB_RADIUS and \
                   -HALF_GRAB_SECTOR_WIDTH < direction - heading < HALF_GRAB_SECTOR_WIDTH

        objects = filter(object_filter, self.arena.objects)
        if objects:
            self._holding = objects[0]
            self._holding.grab()
            self._holding.location = (x + cos(heading) * GRABBER_OFFSET, \
                                      y + sin(heading) * GRABBER_OFFSET)
            return True
        else:
            return False

    def release(self):
        if self._holding is not None:
            self._holding.release()
            self._holding = None
            return True
        else:
            return False

    def see(self, res=(800,600)):
        with self.lock:
            x, y = self.location
            heading = self.heading

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

        return [marker_map(obj) for obj in self.arena.objects if object_filter(obj)]

