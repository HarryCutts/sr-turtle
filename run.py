#!/usr/bin/python2.7

from __future__ import division

import thread, time, pygame
from random import random

from arena import Arena
from display import Display
from markers import Token

NUM_TOKENS = 10

arena = Arena()

for i in range(NUM_TOKENS):
    token = Token(arena, i)
    token.location = (random() * 4 - 2, random() * 4 - 2)
    arena.objects.append(token)

display = Display(arena)

def run_user_code():
    execfile('test.py', {"arena": arena})

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
