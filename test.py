#!/usr/bin/python2.7

from sim_robot import SimRobot
import time

TICK_LENGTH = 0.015

R = SimRobot()

time.sleep(1)
R.set_spin_speed(30)
R.set_speed(60)

while R.location[1] > -240:
    time.sleep(TICK_LENGTH)
    R.tick(TICK_LENGTH)

raw_input()
