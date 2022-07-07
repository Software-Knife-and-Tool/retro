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

if __name__ == '__main__':
    _conf_dict = []
    with open(os.path.join(os.path.dirname(__file__), 'conf.json'), 'r') as file:
        _conf_dict = json.load(file)

    _event = Event()
    _gra_afch = GraAfch(_conf_dict, _event)

    _gra_afch._ncs31x.unblank()
    if _conf_dict["ntp"]:
        _gra_afch._ncs31x.write_rtc(datetime.now().timetuple())

    time.sleep(4)
        
    _sec_timer = RepeatTimer(1, _gra_afch.now, [])
    _sec_timer.start()

    # event loop
    while True:
        event = _event.wait()

