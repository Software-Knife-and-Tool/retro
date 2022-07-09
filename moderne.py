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
from display import Display

VERSION = '0.0.1'

gra_afch = None
event = None
display = None

conf_dict = None

# main
if __name__ == '__main__':
    conf_dict = []
    with open(os.path.join(os.path.dirname(__file__), 'conf.json'), 'r') as file:
        conf_dict = json.load(file)

    event = Event()
    gra_afch = GraAfch(conf_dict, event)
    display = Display(gra_afch, event)
    
    if conf_dict["ntp"]:
        gra_afch._ncs31x.write_rtc(datetime.now().timetuple())

    # inhale deeply
    time.sleep(4)

    # this is for debugging
    signal.signal(signal.SIGINT, lambda s, args : os._exit(0))
    signal.signal(signal.SIGTERM, lambda s, args : os._exit(0))

    gra_afch._ncs31x.unblank()

    display.event_loop()
