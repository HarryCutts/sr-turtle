import sys
from sr import *
import yaml
import threading
from math import pi

with open(sys.argv[1]) as f:
    config = yaml.load(f)

if config['game'] == 'pirate-plunder':
    start_locations = [( 0, -3),
                       ( 3,  0),
                       ( 0,  3),
                       (-3,  0)]
    start_headings = [0.5*pi,
                      pi,
                      -0.5*pi,
                      0]
elif config['game'] == 'ctf':
    start_locations = [(-3.6, -3.6),
                       ( 3.6, -3.6),
                       ( 3.6,  3.6),
                       (-3.6,  3.6)]
    start_headings = [0.25*pi,
                      0.75*pi,
                      -0.75*pi,
                      -0.25*pi]

sim = Simulator(config, foreground=True)

class RobotThread(threading.Thread):
    def __init__(self, zone, fn, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.zone = zone
        self.filename = fn
        self.setDaemon(True)

    def run(self):
        def robot():
            robot_object = SimRobot(sim)
            robot_object.zone = self.zone
            robot_object.location = start_locations[self.zone]
            robot_object.heading = start_headings[self.zone]
            return robot_object
        execfile(self.filename, {'Robot': robot})

for zone, robot in enumerate(sys.argv[2:]):
    if robot == 'empty':
        continue
    thread = RobotThread(zone, robot)
    thread.start()

sim.run()

