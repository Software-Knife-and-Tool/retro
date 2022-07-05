##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## gra-afch controller
##
###########
"""blank the display
"""

from ncs31x import Ncs31x

VERSION = '0.0.1'

if __name__ == '__main__':
    ncs31x = Ncs31x()
    ncs31x.blank()
