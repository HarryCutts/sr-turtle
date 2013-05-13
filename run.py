#!/usr/bin/python2.7

import thread, time

from display import Display
from sim_robot import SimRobot

display = Display()

def run_user_code():
    execfile('test.py')

thread.start_new_thread(run_user_code, ())

while True:
    display.tick(0.03)
    time.sleep(0.03)

input()
