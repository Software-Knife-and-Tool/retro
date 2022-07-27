# -= Vortex Instrument Labs =- - Nixie Tube Smart Clock

_Running Yesterday's Technology Right Into the Ground_

If you're of a certain age, Nixie tube instruments were the ne plus ultra of Cold War high tech cool.

While Nixie tubes are expensive (20+ USD per tube), have a relatively brief lifespan 
(5000 or so hours), and are no longer being generally manufactured, there is a steady supply 
of Cold War era tubes from Eastern Europe.

We here at *Vortex Instrument Labs* appreciate a good anachronism as much or more than the next
person, so we're releasing this code in hopes it'll be of use to someone with an interest in
reviving Cold War instrument technology.

*Retro Industrial Clock* is a Python3 time-of-day clock for the GRA&AFCH NCS31x Raspberry Pi controller.

The original project, https://github.com/afch/NixieClockRaspberryPi, was based on the venerable *wiringpi*
library, which is now deprecated in recent Raspberry Pi releases. *Retro* is a port of similar code to
the *pigpio* daemon.


The documentation for *pigpio* is https://abyz.me.uk/rpi/pigpio/python.html

The hardware can be obtained from http://gra-afch.com

* Retro
  * currently on python 3.9.2
  * web interface for configuration
  * for IN-12 and IN-14 Nixie tubes
  * GRA-AFCH NCS31[24] controller with Raspberry Pi hat
  * many exciting updates planned
  * sadly, many features incomplete and there are hardwired path names throughout
