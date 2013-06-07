from __future__ import division

import pygame

class Arena(object):

    size = (6, 6)

    @property
    def left(s):   return -s.size[0] / 2
    @property
    def right(s):  return s.size[0] / 2
    @property
    def top(s):    return -s.size[1] / 2
    @property
    def bottom(s): return s.size[1] / 2

    def __init__(s, objects=[]):
        s.objects = objects

    ## Public Methods ##

    def contains_point(s, point):
        x, y = point
        return (s.left < x < s.right) and (s.top < y < s.bottom)

    def tick(s, time_passed):
        for o in s.objects:
            o.tick(time_passed)
            # TODO: allow objects without tick methods
