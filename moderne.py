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
import time
import json
import os

from gra_afch import GraAfch

VERSION = '0.0.1'

_gra_afch = None
_conf_dict = None

def now():
    """format the current time onto the display
    """
        
    now_ = datetime.now().strftime("%I%M%S") if _conf_dict["12hour"] else datetime.now().strftime("%H%M%S")

    _gra_afch.display_numerals(
        [_ch_to_int(now_[0]),
         _ch_to_int(now_[1]),
         _ch_to_int(now_[2]),
         _ch_to_int(now_[3]),
         _ch_to_int(now_[4]),
         _ch_to_int(now_[5]),
         8,
         8,
         ])

if __name__ == '__main__':
    _conf_dict = []
    with open(os.path.join(os.path.dirname(__file__), 'conf.json'), 'r') as file:
        _conf_dict = json.load(file)

    _gra_afch = GraAfch(_conf_dict)
    
    time.sleep(4)

    _gra_afch._ncs31x.unblank()
    if _conf_dict["ntp"]:
        _gra_afch._ncs31x.write_rtc(datetime.now().timetuple())
        
    while True:
        for i in range(10):
            _gra_afch.now()
            time.sleep(1)
            
