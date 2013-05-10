#!/usr/bin/python2.7

import time

def ticker(period, robot):
    while True:
        time.sleep(period)
        robot.tick(period)
