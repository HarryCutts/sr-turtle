from __future__ import division

class Arena(object):

    def __init__(s, objects=[]):
        s.objects = objects

    ## Public Methods ##

    def tick(s, time_passed):
        for o in s.objects:
            o.tick(time_passed)
            # TODO: allow objects without tick methods
