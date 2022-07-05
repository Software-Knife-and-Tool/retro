# Vortex Instrument Labs - Moderne Smart Clock

_Beating Yesterday's Technology Senseless_

If you're of a certain age, Nixie tube instruments were the ne plus ultra of Cold War high tech cool.

While Nixie tubes are expensive (20+ USD per tube), have a relatively brief lifespan 
(5000 or so hours), and are no longer being generally manufactured, there is a steady supply 
of Cold War era tubes from Eastern Europe.

We here at *Vortex Instrument Labs* appreciate a good anachronism as much or more than the next
person, so we're releasing this code in hopes it'll be of use to someone with an interst in
reviving Cold War instrument technology.

*Moderne* is a Python3 time-of-day clock for the GRA&AFCH NCS31x Raspberry Pi controller.

The original project was based on the venerable *wiringpi* library, which is now deprecated
in recent Raspberry Pi releases. *Moderne* is a port of similar code to the *pigpio* daemon.

The documentation for *pigpio* is https://abyz.me.uk/rpi/pigpio/python.html

The hardware can be obtained from http://gra-afch.com

* Moderne
  * currently on python 3.9
  * for IN-12 and IN-14 tubes
  * GRA-AFCH NCS31[24] controller with Raspberry Pi hat
  * many exciting updates planned
