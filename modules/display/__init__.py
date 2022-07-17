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
from time import localtime, strftime, mktime
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

    _sec_timer = None
    _blank_timer = None
    
    _is_blank = None

    _tick_event = None
    _blank_event = None
    _unblank_event = None

    _state = None
    _state_machine = None

    def clean_display(self):
        display = [0 for _ in range(8)]
        
        self._gra_afch._ncs31x.unblank()
        self._gra_afch._ncs31x.backlight([0, 0, 0])

        for _ in range(10):
            for ch in range(10):
                for tube in range(8):
                    display[tube] = ch
                self._gra_afch.display_numerals(display)
                time.sleep(0.01)
                self._gra_afch._ncs31x.clear()
                
    def blank_display(self):
        self._event.send(self._blank_event)

    def unblank_display(self):
        self._event.send(self._unblank_event)

    def _blank(self):
        self._is_blank = True
        self._gra_afch._ncs31x.blank()
        self._gra_afch._ncs31x.backlight([0, 0, 0])

    def _unblank(self):
        self._is_blank = False
        self._gra_afch._ncs31x.unblank()
        self._gra_afch._ncs31x.backlight(self._conf_dict["back-light"])

    def _date(self):
        self._gra_afch._ncs31x.blank()
        time.sleep(.25)
        self._gra_afch._ncs31x.unblank()
        for _ in range(5):
            time.sleep(1)
            self._gra_afch.date()
        self._gra_afch._ncs31x.clear()
        if self._is_blank:
            self._gra_afch._ncs31x.blank()

    def time(self):
        return datetime.fromtimestamp(mktime(self._gra_afch._ncs31x.read_rtc(False)))

    # simple state machine
    def state_machine(self, event):
        key = list(event.keys())[0]
        # print(self._state, end=" ")
        # print(event)
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
        self._conf_dict = gra_afch._conf_dict;
        
        self._event = event
        self._gra_afch = gra_afch

        self._state = 'time'
        self._state_machine = {
            'blank': dict([
                ( 'tick',        [ lambda self: None, 'blank' ] ),
                ( 'blank',       [ lambda self: None, 'blank' ] ),
                ( 'unblank',     [ lambda self: Display._unblank(self), 'time' ] ),
                ( 'up-button',   [ lambda self: Display._unblank(self), 'time' ] ),
                ( 'down-button', [ lambda self: Display._unblank(self), 'time' ] ),
                ( 'mode-button', [ lambda self: Display._unblank(self), 'time' ] ),
            ]),
            'date': dict([
                ( 'tick',        [ lambda self: Display._date(self), 'date' ] ),
                ( 'blank',       [ lambda self: Display._blank(self), 'date' ] ),
                ( 'unblank',     [ lambda self: Display._unblank(self), 'date' ] ),
                ( 'up-button',   [ lambda self: None, 'time' ] ),
                ( 'down-button', [ lambda self: None, 'time' ] ),
                ( 'mode-button', [ lambda self: None, 'time' ] ),
            ]),
            'time': dict([
                ( 'tick',        [ lambda self: GraAfch.time(self._gra_afch), 'time' ] ),
                ( 'blank',       [ lambda self: Display._blank(self), 'blank' ] ),
                ( 'unblank',     [ lambda self: Display._unblank(self), 'time' ] ),
                ( 'up-button',   [ lambda self: None, 'time' ] ),
                ( 'down-button', [ lambda self: None, 'time' ] ),
                ( 'mode-button', [ lambda self: Display._date(self), 'date' ] ),
            ]),
        }

        if self._conf_dict['ntp']:
            gra_afch._ncs31x.write_rtc(datetime.now().timetuple())

        self._tick_event = event.event('tick', None)
        self._blank_event = event.event('blank', None)
        self._unblank_event = event.event('unblank', None)
                    
        # seconds timer
        self._sec_timer = RepeatTimer(1, lambda: event.send(self._tick_event))
        self._sec_timer.start()

        # display timeout
        if self._conf_dict['blank-timeout']:
            tm = self._conf_dict['blank-timeout']
            self._blank_timer = RepeatTimer(tm, lambda: event.send(self._blank_event))
            self._blank_timer.start()

