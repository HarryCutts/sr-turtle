#!/usr/bin/python2.7

import pygame, sys, os, thread
from pygame.locals import *
from math import sin, cos, radians

from ticker import *

class SimRobot:
    _window_size = (640, 480)
    location = (0, 0)
    heading = 0

    _spin_speed = 0  # degrees/s
    _speed = 0       # in pixels/s

    ## Constructor ##

    def __init__(s):
        pygame.init()
        s._window = pygame.display.set_mode(s._window_size)
        pygame.display.set_caption("SR Robot Simulator")
        s._screen = pygame.display.get_surface()
        s._robot_png = pygame.image.load("robot.png").convert()
        s._draw()

    ## Internal methods ##

    def _get_bounds(s):
        w, h = s._window_size
        rx, ry = s.location
        x = w / 2 + rx
        y = h / 2 + ry
        return Rect(x - 25, y - 25, 50, 50)

    def _draw(s):
        ww, wh = s._window_size
        rx, ry = s.location
        robot_surface = pygame.transform.rotate(s._robot_png, s.heading)
        rw, rh = robot_surface.get_size()
        screen_location = (rx + (ww - rw) / 2., ry + (wh - rh) / 2.)
        s._screen.fill((0, 0, 0))
        s._screen.blit(robot_surface, screen_location)
        pygame.display.flip()

    ## "Public" methods ##

    def set_spin_speed(s, spin_speed):
        s._spin_speed = spin_speed

    def set_speed(s, speed):
        s._speed = speed

    def start(s):
        thread.start_new(ticker, (0.015, s))

    def tick(s, time_passed):
        s.heading += s._spin_speed * time_passed
        dist = s._speed * time_passed
        heading_rads = radians(s.heading)
        xmod = cos(heading_rads) * dist
        ymod = -sin(heading_rads) * dist
        x, y = s.location
        s.location = (x + xmod, y + ymod)
        s._draw()
