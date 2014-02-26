from sr import *

try:
    sim = Simulator(num_tokens=5)
except NameError:
    print "This script must be run with `python -m` (i.e. `python -m tests.motor_board_serialnum`)"

R = SimRobot(sim)

assert type(R.motors[0].serialnum) == str, "Motor.serialnum must be a string"
print R.motors[0]
