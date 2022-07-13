##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## display controller
##
###########
"""Manage GRA-AFCH NCS31X display

See module ncs31x for display board interface.
See module gra_afch for display board functions.

Classes:

    Display
    RepeatTimer(Timer)

Functions:

    blank_display(self)
    date_display(self)
    event_loop()
    state_machine(event)
    unblank_display(self)
    version()

Misc variables:

    _conf_dict
    _sec_timer
    _blank_timer

"""

import json
import time
import pigpio
import os

from datetime import datetime
from time import localtime, strftime
from threading import Timer

from event import Event
from gra_afch import GraAfch
from ncs31x import Ncs31x

class RepeatTimer(Timer):
    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def callback(self):
        self.f(*self.args, **self.kwargs)
        self.start()

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()
        
class Display:
    """display utilities
    """

    VERSION = '0.0.1'
    
    _gra_afch = None
    _event = None
    _conf_dict = None

    _sec_event = None
    _sec_timer = None

    _is_blank = None
    _blank_event = None
    _blank_timer = None

    _state = None

    _state_machine = None

    def blank_display(self):
        self._is_blank = True
        self._gra_afch._ncs31x.blank()
        self._gra_afch._ncs31x.backlight([0, 0, 0])

    def unblank_display(self):
        self._is_blank = False
        self._gra_afch._ncs31x.unblank()
        self._gra_afch._ncs31x.backlight(self._conf_dict["back-light"])

    def date_display(self):
        self._gra_afch._ncs31x.blank()
        time.sleep(.25)
        self._gra_afch._ncs31x.unblank()
        for _ in range(5):
            time.sleep(1)
            self._gra_afch.date()
        self._gra_afch._ncs31x.clear()
        if self._is_blank:
            self._gra_afch._ncs31x.blank()

    # simple state machine
    def state_machine(self, event):
        key = list(event.keys())[0]

        self._state_machine[self._state][key][0](self)
        self._state = self._state_machine[self._state][key][1]

    # main event loop
    def event_loop(self):
        while True:
            event = self._event.wait()
            self.state_machine(event)

    def __init__(self, gra_afch, event):
        """initialize the display module
        """

        self._event = event
        self._gra_afch = gra_afch

        self._conf_dict = gra_afch._conf_dict;

        self._state = "time"
        self._state_machine = {
            'blank': dict([
                ( 'tick',        [ lambda self: None, 'blank' ] ),
                ( 'blank',       [ lambda self: None, 'blank' ] ),
                ( 'up-button',   [ lambda self: Display.unblank_display(self), 'time' ] ),
                ( 'down-button', [ lambda self: Display.unblank_display(self), 'time' ] ),
                ( 'mode-button', [ lambda self: Display.unblank_display(self), 'time' ] ),
            ]),
            'date': dict([
                ( 'tick',        [ lambda self: Display.date_display(self), 'date' ] ),
                ( 'blank',       [ lambda self: Display.blank_display(self), 'date' ] ),
                ( 'up-button',   [ lambda self: None, 'time' ] ),
                ( 'down-button', [ lambda self: None, 'time' ] ),
                ( 'mode-button', [ lambda self: None, 'time' ] ),
            ]),
            'time': dict([
                ( 'tick',        [ lambda self: GraAfch.time(self._gra_afch), 'time' ] ),
                ( 'blank',       [ lambda self: Display.blank_display(self), 'blank' ] ),
                ( 'up-button',   [ lambda self: None, 'time' ] ),
                ( 'down-button', [ lambda self: None, 'time' ] ),
                ( 'mode-button', [ lambda self: Display.date_display(self), 'time' ] ),
            ]),
        }

        if self._conf_dict["ntp"]:
            gra_afch._ncs31x.write_rtc(datetime.now().timetuple())

        # seconds timer
        self._sec_event = event.event("tick", None)
        self._sec_timer = RepeatTimer(1, lambda: event.send(self._sec_event))
        self._sec_timer.start()

        # display timeout
        if self._conf_dict["blank-timeout"]:
            tm = self._conf_dict["blank-timeout"]
            self._blank_event = event.event("blank", None)
            self._blank_timer = RepeatTimer(tm, lambda: event.send(self._blank_event))
            self._blank_timer.start()

