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

from threading import Timer

import time
import json
import os
import sys
import signal

from gra_afch import GraAfch
from event import Event
from display import Display

class Moderne:
    """moderne class
    """
    
    gra_afch = None
    event = None
    display = None

    _conf_dict = None

    def __init__(self, conf_dict):
        self.event = Event()
        self.gra_afch = GraAfch(conf_dict, self.event)
        self.display = Display(self.gra_afch, self.event)

# main
if __name__ == '__main__':

    # this is for debugging
    signal.signal(signal.SIGINT, lambda s, args : os._exit(0))
    signal.signal(signal.SIGTERM, lambda s, args : os._exit(0))

    conf_dict = []
    with open(os.path.join(os.path.dirname(__file__), '../etc/moderne.json'), 'r') as file:
        conf_dict = json.load(file)

    moderne = Moderne(conf_dict)
    
    # inhale deeply
    time.sleep(4)

    moderne.display.unblank_display()
    moderne.display.event_loop()
    
