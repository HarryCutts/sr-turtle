#!/usr/bin/python2.7

from __future__ import division

import thread, time, pygame

from arena import Arena
from display import Display
from sim_robot import SimRobot

arena = Arena()
display = Display(arena)

def run_user_code():
    execfile('test.py')

thread.start_new_thread(run_user_code, ())

clock = pygame.time.Clock()

done = False

while done == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    display.tick(1/30)
    clock.tick(30)

pygame.quit()
