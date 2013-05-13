#!/usr/bin/python2.7

from sim_robot import SimRobot

R = SimRobot(display)

R.motors[0].target = 1
R.motors[1].target = 2

while True:
    sl, sr = input("Enter two new speeds:")
    R.motors[0].target = sl
    R.motors[1].target = sr
