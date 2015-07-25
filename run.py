import sys
import yaml
import threading
import argparse
from math import pi

from sr.robot import *

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config',
                    type=argparse.FileType('r'),
                    default='games/two_colours.yaml')
parser.add_argument('robot_scripts',
                    type=argparse.FileType('r'),
                    nargs='*')
args = parser.parse_args()

robot_scripts = args.robot_scripts
prompt = "Enter the names of the Python files to run, separated by commas: "
while not robot_scripts:
    robot_script_names = raw_input(prompt).split(',')
    if robot_script_names == ['']: continue
    robot_scripts = [open(s.strip()) for s in robot_script_names]

with args.config as f:
    config = yaml.load(f)

sim = Simulator(config, foreground=True)

class RobotThread(threading.Thread):
    def __init__(self, zone, script, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.zone = zone
        self.script = script
        self.setDaemon(True)

    def run(self):
        def robot():
            with sim.arena.physics_lock:
                robot_object = SimRobot(sim)
                robot_object.zone = self.zone
                robot_object.location = sim.arena.start_locations[self.zone]
                robot_object.heading = sim.arena.start_headings[self.zone]
                return robot_object

        exec self.script in {'Robot': robot}

for zone, robot in enumerate(robot_scripts):
    thread = RobotThread(zone, robot)
    thread.start()

sim.run()

