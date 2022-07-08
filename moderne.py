##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## moderne
##
###########

from datetime import datetime
from threading import Timer

import time
import json
import os
import sys
import signal

from gra_afch import GraAfch
from event import Event

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

VERSION = '0.0.1'

_gra_afch = None
_event = None

_conf_dict = None
_sec_timer = None
_sec_timer_update = None

_blank_timeout = None

if __name__ == '__main__':
    _conf_dict = []
    with open(os.path.join(os.path.dirname(__file__), 'conf.json'), 'r') as file:
        _conf_dict = json.load(file)

    _event = Event()
    _gra_afch = GraAfch(_conf_dict, _event)

    if _conf_dict["ntp"]:
        _gra_afch._ncs31x.write_rtc(datetime.now().timetuple())

    # breathing room
    time.sleep(4)

    # display timeout
    if _conf_dict["display_timeout"]:
        tm = _conf_dict["display_timeout"]
        _blank_timer = RepeatTimer(tm, _gra_afch._ncs31x.blank, [])
        _blank_timer.start()

    # seconds timer
    _sec_timer = RepeatTimer(1, lambda: _gra_afch.now() if _sec_timer_update else False, [])
    _sec_timer_update = True
    _sec_timer.start()

    # this is for debuuging
    signal.signal(signal.SIGINT, lambda s, args : _event.send(_event.event("exit", "")))

    _gra_afch._ncs31x.unblank()
    
    # event loop
    while True:
        event = _event.wait()
        if "exit" in event:
            _gra_afch._ncs31x.blank()
            os._exit(0)

        if "up-button" in event:
            _gra_afch._ncs31x.unblank()
            _blank_timer.cancel()
            _blank_timer.start()
            
        if "down-button" in event:
            _gra_afch._ncs31x.unblank()
            _blank_timer.cancel()
            _blank_timer.start()
                    
        if "mode-button" in event:
            _sec_timer_update = False
            for i in range(3):
                _gra_afch._ncs31x.blank()
                time.sleep(.25)
                _gra_afch._ncs31x.unblank()
                time.sleep(.25)
                _gra_afch.display_numerals([0 for x in range(8)])

