from sr.robot import *

import time

SEARCHING, DRIVING = range(2)

R = Robot()

token_filter = lambda m: m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER)

def drive(speed, seconds):
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

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
            turn(25, 0.3)
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
                    turn(50, 0.5)
                    drive(50, 1)
                    R.release()
                    drive(-50, 0.5)
                else:
                    print "Aww, I'm not close enough."
                exit()

            elif -15 <= m.rot_y <= 15:
                print "Ah, that'll do."
                drive(50, 0.5)

            elif m.rot_y < -15:
                print "Left a bit..."
                turn(-12.5, 0.5)

            elif m.rot_y > 15:
                print "Right a bit..."
                turn (12.5, 0.5)
