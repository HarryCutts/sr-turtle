import sys
from sr import *
import yaml
import threading
from math import pi

with open(sys.argv[1]) as f:
    config = yaml.load(f)

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
            robot_object.location = sim.arena.start_locations[self.zone]
            robot_object.heading = sim.arena.start_headings[self.zone]
            return robot_object
        execfile(self.filename, {'Robot': robot})

for zone, robot in enumerate(sys.argv[2:]):
    if robot == 'empty':
        continue
    thread = RobotThread(zone, robot)
    thread.start()

sim.run()

