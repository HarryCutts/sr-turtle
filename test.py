#!/usr/bin/python2.7

from sim_robot import SimRobot
import time

R = SimRobot()
R.start()

while True:
    time.sleep(4)
    R.set_speed(0)
    R.set_spin_speed(45)
    time.sleep(2)
    R.set_spin_speed(0)
    R.set_speed(50)
