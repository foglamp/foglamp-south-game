South plugin for Raspberry Pi Enviro pHAT for use in IoT lab game.

This pugin has been designed for a game that is played with EnviroP pHAT's mounted
on radio control cars. It feeds foglamp with readings that equate to points scored
in the game my drivng the car and reacting to lights.

The scoring works as follows:

You score points for forward and reverse acceleration values, these
are weighted as a tenth of a point per G of acceleration per tenth
of a second, accelerate at 0.2 G for a second and you get 1 point.

You score points for lateral acceleration values, i.e. cornering
force. These are weighted as three tenths of a point per G of
acceleration per tenth of a second, corner at 0.2 G for a second
and you get 3 point.

You get 1 bonus point for passing under a red light, note, if you
stop then you do not get any more points until you move off from
the red light and come back to it

You get 2 bonus points for passing under a green light, note, if
you stop then you do not get any more points until you move off
from the green light and come back to it

You get 3 bonus points for passing under a blue light, note, if you
stop then you do not get any more points until you move off from
the blue light and come back to it

If you are stationary under a light when it changes you do not get
the points for the new colour

If you roll the car, for example due to heavy cornering, you loose
10 points

