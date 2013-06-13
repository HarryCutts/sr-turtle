#!/usr/bin/python2.7

from __future__ import division

import thread, time, pygame
from random import random

from arena import Arena
from display import Display
from sim_robot import SimRobot
from markers import Token
from vision import *

NUM_TOKENS = 10

arena = Arena()

for i in range(NUM_TOKENS):
    token = Token(arena, create_marker_info_by_type(MARKER_TOKEN, i))
    token.location = (random() * 4 - 2, random() * 4 - 2)
    arena.objects.append(token)

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
