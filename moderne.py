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

import time
import datetime
import json
import os

from gra_afch import GraAfch

VERSION = '0.0.1'

_gra_afch = None
_conf_dict = None

if __name__ == '__main__':

    _conf_dict = []
    with open(os.path.join(os.path.dirname(__file__), 'conf.json'), 'r') as file:
        _conf_dict = json.load(file)

    _gra_afch = GraAfch(_conf_dict)
    
    time.sleep(4)

    _gra_afch._ncs31x.unblank()
    print(_gra_afch._ncs31x.read_rtc(_conf_dict["12hour"]))

    while True:
        for i in range(10):
            _gra_afch.now()
            time.sleep(1)
            
