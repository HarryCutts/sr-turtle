Student Robotics Robot Simulator
================================

This is a simple, portable robot simulator developed for [Student Robotics](https://studentrobotics.org), originally for a summer school aimed at 15-18 year olds. It allows competitors to test their code for such things as navigation and item finding while remaining similar to the [Student Robotics API][sr-api] which they are using to control their real hardware.

Installing and running
----------------------

The simulator requires a Python 2.7 installation, and the [pygame](http://pygame.org/) library. Once those are installed, simply run the `test.py` script to test out the simulator.

Writing a program
-----------------

Keep your programs in the directory containing the simulator files, so that the `sr` module can be imported.

An example program can be found in `test.py`, which implements a simple state machine and does a pretty shoddy job of finding and picking up tokens. A template is also provided in `template.py`.

Where a program using the SR API would begin:

```python
from sr import *

R = Robot()
```

a program using the simulator API begins:

```python
from sr import *

sim = Simulator()
R = SimRobot(sim)
```

`Simulator()` creates a new simulator, with an 8 metre square arena containing 5 tokens and 27 wall markers, just like the real SR arena. (The `size` and `num_tokens` parameters can be used to change these.) The `SimRobot` object replaces the `Robot` object, and must have a `Simulator` object passed to its constructor.

After this, calls can be made to the simulator API through the `R` object.

Robot API
---------

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

### Motors ###

The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the spot at one quarter of full power, one might write the following:

```python
R.motors[0].m0 = 25
R.motors[0].m1 = -25
```

### The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, call the `R.release` method.

Cable-tie flails are not implemented.

### Vision ###

To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can only see markers which it is facing towards.

Each `Marker` object has the following attributes:

* `info`: a `MarkerInfo` object describing the marker itself. Has the following attributes:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN` or `MARKER_ARENA`).
  * `offset`: offset of the numeric code of the marker from the lowest numbered marker of its type. For example, token number 3 has the code 43, but offset 3.
* `centre`: the location of the marker in polar coordinates, as a `PolarCoord` object. Has the following attributes:
  * `length`: the distance from the centre of the robot to the object (in metres).
  * `rot_y`: rotation about the Y axis in degrees.
* `timestamp`: the time at which the marker was seen (when `R.see` was called).

For example, the following code lists all of the markers the robot can see:

```python
markers = R.see()
print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type == MARKER_TOKEN:
        print " - Token {0} is {1} metres away".format( m.info.offset, m.dist )
    elif m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is {1} metres away".format( m.info.offset, m.dist )
```

[sr-api]: https://studentrobotics.org/docs/programming/sr/
