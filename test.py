#!/usr/bin/python2.7

from sim_robot import SimRobot

R = SimRobot(arena)
markers = R.see()

print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type == MARKER_TOKEN:
        print " - Token {0} is {1} metres away".format(m.info.offset, m.dist)
    if m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is at {1} degrees".format(m.info.offset, m.rot_y)
