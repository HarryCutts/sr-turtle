#!/usr/bin/python2.7

from sim_robot import SimRobot

import time

SEARCHING, DRIVING = range(2)

R = SimRobot(arena)

def token_filter(m):
    return m.info.marker_type == MARKER_TOKEN

def drive(speed, seconds):
    global R
    R.motors[0].target = speed
    R.motors[1].target = speed
    time.sleep(seconds)
    R.motors[0].target = 0
    R.motors[1].target = 0

def turn(speed, seconds):
    global R
    R.motors[0].target = speed
    R.motors[1].target = -speed
    time.sleep(seconds)
    R.motors[0].target = 0
    R.motors[1].target = 0

state = SEARCHING

while True:
    if state == SEARCHING:
        print "Searching..."
        tokens = filter(token_filter, R.see())
        if len(tokens) > 0:
            m = tokens[0]
            print "Token sighted. {0} is {1}m away, bearing {2} degrees." \
                  .format(m.info.offset, m.dist, m.rot_y)
            state = DRIVING

        else:
            print "Can't see anything."
            turn(0.5, 0.3)
            time.sleep(0.2)

    elif state == DRIVING:
        print "Aligning..."
        tokens = filter(token_filter, R.see())
        if len(tokens) == 0:
            state = SEARCHING

        else:
            m = tokens[0]
            if m.dist < 0.4:
                print "Found it!"
                if R.grab():
                    print "Gotcha!"
                    turn(1, 0.5)
                    drive(1, 1)
                    R.release()
                    drive(-1, 0.5)
                else:
                    print "Aww, I'm not close enough."
                exit()

            elif -15 <= m.rot_y <= 15:
                print "Ah, that'll do."
                drive(1.0, 0.5)

            elif m.rot_y < -15:
                print "Left a bit..."
                turn(-0.25, 0.5)

            elif m.rot_y > 15:
                print "Right a bit..."
                turn (0.25, 0.5)
