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

Classes:

    Display

Functions:

    state_machine(event)
    event_loop()

Misc variables:

    _conf_dict
    _sec_timer
    _blank_timer
"""

import json
import time
import pigpio
import os

from time import localtime, strftime
from threading import Timer

from event import Event
from gra_afch import GraAfch
from ncs31x import Ncs31x

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class Display:
    """display utilities
    """
    _gra_afch = None
    _event = None
    _conf_dict = None

    _sec_event = None
    _sec_timer = None
    
    _blank_event = None
    _blank_timer = None

    _state = "time"
    _state_machine = None

    def date_display(self):
        self._gra_afch._ncs31x.unblank()
        self._gra_afch.date()
                            
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

        self._state_machine = {
            'blank': dict([
                ( 'tick',        [ lambda self: None, 'blank' ] ),
                ( 'blank',       [ lambda self: None, 'blank' ] ),
                ( 'up-button',   [ lambda self: Ncs31x.unblank(self._gra_afch._ncs31x), 'time' ] ),
                ( 'down-button', [ lambda self: Ncs31x.unblank(self._gra_afch._ncs31x), 'time' ] ),
                ( 'mode-button', [ lambda self: Ncs31x.unblank(self._gra_afch._ncs31x), 'time' ] ),
            ]),
            'date': dict([
                ( 'tick',        [ lambda self: Display.date_display(self), 'date' ] ),
                ( 'blank',       [ lambda self: Ncs31x.blank(self), 'date' ] ),
                ( 'up-button',   [ lambda self: None, 'time' ] ),
                ( 'down-button', [ lambda self: None, 'time' ] ),
                ( 'mode-button', [ lambda self: None, 'time' ] ),
            ]),
            'time': dict([
                ( 'tick',        [ lambda self: GraAfch.time(self._gra_afch), 'time' ] ),
                ( 'blank',       [ lambda self: Ncs31x.blank(self._gra_afch._ncs31x), 'blank' ] ),
                ( 'up-button',   [ lambda self: None, 'time' ] ),
                ( 'down-button', [ lambda self: None, 'time' ] ),
                ( 'mode-button', [ lambda self: Display.date_display(self), 'date' ] ),
            ]),
        }

        # seconds timer
        self._sec_event = event.event("tick", None)
        self._sec_timer = RepeatTimer(1, lambda: event.send(self._sec_event))
        self._sec_timer.start()

        # display timeout
        if self._conf_dict["display_timeout"]:
            tm = self._conf_dict["display_timeout"]
            self._blank_event = event.event("blank", None)
            self._blank_timer = RepeatTimer(tm, lambda: event.send(self._blank_event))
            self._blank_timer.start()

