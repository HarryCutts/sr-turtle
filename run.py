#!/usr/bin/python2.7

import thread, time, pygame

from display import Display
from sim_robot import SimRobot

display = Display()

def run_user_code():
    execfile('test.py')

thread.start_new_thread(run_user_code, ())

clock = pygame.time.Clock()

done = False

while done == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    display.tick(0.03)
    clock.tick(30)

pygame.quit()
