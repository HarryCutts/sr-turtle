#!/usr/bin/python2.7

from __future__ import division

import time, exceptions
from math import pi, sin, cos, degrees, hypot, atan2

from game_object import GameObject
from vision import Marker, Point, PolarCoord, create_marker_info_by_type, MARKER_ROBOT

import pypybox2d

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

    def __init__(self, robot):
        self._robot = robot
        self.serialnum = "SIM_MBv4"

        self.m0 = MotorChannel(robot)
        self.m1 = MotorChannel(robot)

    def __repr__(self):
        return "Motor( serialnum = \"{0}\" ) (Simulated Motor Board v4)" \
               .format(self.serialnum)

class SimRobot(GameObject):
    width = 0.45

    surface_name = 'sr/robot.png'

    _holding = None

    ## Constructor ##

    @property
    def location(self):
        with self.lock:
            return self._body.position

    @location.setter
    def location(self, new_pos):
        if self._body is None:
            return # Slight hack: deal with the initial setting from the constructor
        with self.lock:
            self._body.position = new_pos

    @property
    def heading(self):
        with self.lock:
            return self._body.angle

    @heading.setter
    def heading(self, _new_heading):
        if self._body is None:
            return # Slight hack: deal with the initial setting from the constructor
        with self.lock:
            self._body.angle = _new_heading

    @property
    def marker_info(self):
        return create_marker_info_by_type(MARKER_ROBOT, self.zone)

    def __init__(self, simulator):
        self._body = None
        self.zone = 0
        GameObject.__init__(self, simulator.arena)
        self.motors = [Motor(self)]
        make_body = simulator.arena._physics_world.create_body
        half_width = self.width * 0.5
        with self.arena.physics_lock:
            self._body = make_body(position=(0, 0),
                                   angle=0,
                                   linear_damping=0.0,
                                   angular_damping=0.0,
                                   type=pypybox2d.body.Body.DYNAMIC)
            self._body.create_polygon_fixture([(-half_width, -half_width),
                                               ( half_width, -half_width),
                                               ( half_width,  half_width),
                                               (-half_width,  half_width)],
                                              density=500*0.12) # MDF @ 12cm thickness
        simulator.arena.objects.append(self)


    ## Internal methods ##

    def _apply_wheel_force(self, y_position, power):
        location_world_space = self._body.get_world_point((0, y_position))
        force_magnitude = power * 0.6
        # account for friction
        frict_world = self._body.get_linear_velocity_from_local_point((0, y_position))
        frict_x, frict_y = self._body.get_local_vector(frict_world)
        force_magnitude -= frict_x * 50.2
        force_world_space = (force_magnitude * cos(self.heading),
                             force_magnitude * sin(self.heading))
        self._body.apply_force(force_world_space, location_world_space)

    ## "Public" methods for simulator code ##

    def tick(self, time_passed):
        with self.lock, self.arena.physics_lock:
            half_width = self.width * 0.5
            # left wheel
            self._apply_wheel_force(-half_width, self.motors[0].m0.power)
            # right wheel
            self._apply_wheel_force( half_width, self.motors[0].m1.power)
            # kill the lateral velocity
            right_normal = self._body.get_world_vector((0, 1))
            lateral_vel = (right_normal.dot(self._body.linear_velocity) *
                           right_normal)
            impulse = self._body.mass * -lateral_vel
            self._body.apply_linear_impulse(impulse, self._body.world_center)

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
            return (o.grabbable and
                    hypot(rel_x, rel_y) <= GRAB_RADIUS and
                    -HALF_GRAB_SECTOR_WIDTH < direction - heading < HALF_GRAB_SECTOR_WIDTH and
                    not o.grabbed)

        objects = filter(object_filter, self.arena.objects)
        if objects:
            self._holding = objects[0]
            if hasattr(self._holding, '_body'):
                with self.lock, self.arena.physics_lock:
                    self._holding_joint = self._body._world.create_weld_joint(self._body,
                                                                              self._holding._body,
                                                                              local_anchor_a=(GRABBER_OFFSET, 0),
                                                                              local_anchor_b=(0, 0))
            self._holding.grab()
            return True
        else:
            return False

    def release(self):
        if self._holding is not None:
            self._holding.release()
            if hasattr(self._holding, '_body'):
                with self.lock, self.arena.physics_lock:
                    self._body.world.destroy_joint(self._holding_joint)
                self._holding_joint = None
            self._holding = None
            return True
        else:
            return False

    def see(self, res=(800,600)):
        with self.lock:
            x, y = self.location
            heading = self.heading

        acq_time = time.time()

        MOTION_BLUR_SPEED_THRESHOLD = 5

        def robot_moving(o):
            vx, vy = o._body.linear_velocity
            return hypot(vx, vy) > MOTION_BLUR_SPEED_THRESHOLD

        def motion_blurred(o):
            # Simple approximation: we can't see anything if either it's moving
            # or we're moving. This doesn't handle tokens grabbed by other robots
            # but Sod's Law says we're likely to see those anyway.
            return (robot_moving(self) or
                    isinstance(o, SimRobot) and robot_moving(o))

        def object_filter(o):
            # Choose only marked objects within the field of view
            direction = atan2(o.location[1] - y, o.location[0] - x)
            return (o.marker_info != None and
                    o is not self and
                    -HALF_FOV_WIDTH < direction - heading < HALF_FOV_WIDTH and
                    not motion_blurred(o))

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

