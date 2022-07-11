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
"""Manage GRA-AFCH NCS31X hardware

See module ncs31x for display board interface.

Classes:
    GraAfch

Functions:

    buttons()
    date()
    time()
    display_numerals(digits)

    update_backlight(color)

Misc variables:

    _conf_dict
    _dots
    _lock
    _tube_mask
"""

import json
import time
import pigpio
import os

from time import localtime, strftime
from threading import Timer
from event import Event

from ncs31x import Ncs31x

class GraAfch:
    """board utilities
    """
    VERSION = '0.0.1'

    # seconds
    _DEBOUNCE_DELAY = 0.015
    _TOTAL_DELAY = 0.017

    # events
    _INT_EDGE_RISING = 1
    _INT_EDGE_FALLING = 0

    _mode_cb = None
    _up_cb = None
    _down_cb = None

    _mode_event = None
    _up_event = None
    _down_event = None
        
    # ncs31x
    _ncs31x = None
    _gpio = None

    # event framework
    _event = None

    # configuration
    _conf_dict = None

    # display
    _dots = None
    _tube_mask = [255 for _ in range(8)]

    # def string_to_color(str_):
    #    def ctoi_(nib):#
    #        nval = 0
    #
    #        if nib >= '0' & nib <= '9':
    #            nval = nib - '0'
    #        elif nib >= 'a' & nib <= 'f':
    #            nval = nib - 'a' + 10;
    #        elif (nib >= 'A' & nib <= 'F'):
    #            nval = nib - 'A' + 10
    #        else:
    #            nval = -1
    #        return nval
    #
    #    def channel_(msn, lsn):
    #        m = ctoi(msn);
    #        l = ctoi(lsn);
    #
    #        return (m < 0 | l < 0) if -1 else (m << 4) + l
    #
    #    r = channel(str[0], str[1])
    #    g = channel(str[2], str[3])
    #    b = channel(str[4], str[5])
    #
    #    return [r, g, b];

    def update_backlight(self, color):
        """change the backlight color
        """
        
        def scale_(nval):
            return int(nval * (100 / 255))

        self._ncs31x.backlight(
            [scale_(color[0]),
             scale_(color[1]),
             scale_(color[2])])

    def display_numerals(self, digits):
        """stuff the tubes from decimal string
        """
        
        def tubes_(str_, start):
            tube_map_ = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 0]

            def digit_(digit):
                return 10 if digit == 0x20 else digit

            bits = (tube_map_[digit_(str_[start])]) << 20
            bits |= (tube_map_[digit_(str_[start - 1])]) << 10
            bits |= (tube_map_[digit_(str_[start - 2])])

            return bits

        def dots_(bits):
            if self._dots:
                bits |= Ncs31x._LOWER_DOTS_MASK
                bits |= Ncs31x._UPPER_DOTS_MASK
            else:
                bits &= ~Ncs31x._LOWER_DOTS_MASK
                bits &= ~Ncs31x._UPPER_DOTS_MASK

            return bits

        def fmt_(nval, buffer, start, off):
            buffer[start] = (nval >> 24 & 0xff) & self._tube_mask[off]
            buffer[start + 1] = ((nval >> 16) & 0xff) & self._tube_mask[off + 1]
            buffer[start + 2] = ((nval >> 8) & 0xff) & self._tube_mask[off + 2]
            buffer[start + 3] = (nval & 0xff) & self._tube_mask[off + 3]

            return buffer

        buffer = [0 for _ in range(8)]

        left = tubes_(digits, Ncs31x._LEFT_REPR_START)
        left = dots_(left)
        fmt_(left, buffer, Ncs31x._LEFT_BUFFER_START, 0)

        right = tubes_(digits, Ncs31x._RIGHT_REPR_START)
        right = dots_(right)
        fmt_(right, buffer, Ncs31x._RIGHT_BUFFER_START, 4)

        self._ncs31x.blank()
        self._ncs31x.display(buffer)
        self._ncs31x.unblank()

    def time(self):
        """format the current time onto the display
        """
        
        time = self._ncs31x.read_rtc(self._conf_dict["time-format"] == "12hour")
        if self._conf_dict["zero-blank"]:
            self.display_numerals(
                [time.tm_hour // 10 if time.tm_hour // 10 else 0x20,
                 time.tm_hour % 10,
                 time.tm_min // 10 if time.tm_hour // 10 else 0x20,
                 time.tm_min % 10,
                 time.tm_sec // 10,
                 time.tm_sec % 10,
                 8,
                 8,
                 ])
        else:
            self.display_numerals(
                [time.tm_hour // 10,
                 time.tm_hour % 10,
                 time.tm_min // 10,
                 time.tm_min % 10,
                 time.tm_sec // 10,
                 time.tm_sec % 10,
                 8,
                 8,
                 ])

            
    def date(self):
        """format the current date  onto the display
        """
        date = self._ncs31x.read_rtc(self._conf_dict["date-format"])
        
        if self._conf_dict["zero-blank"]:
            self.display_numerals(
                [date.tm_mday // 10 if time.tm_mday // 10 else 0x20,
                 date.tm_mday % 10,
                 date.tm_mon // 10 if time.tm_mon // 10 else 0x20,
                 date.tm_mon % 10,
                 (date.tm_year - 2000) // 10,
                 (date.tm_year - 2000) % 10,
                 8,
                 8,
                 ])
        else:
            self.display_numerals(
                [date.tm_mday // 10,
                 date.tm_mday % 10,
                 date.tm_mon // 10,
                 date.tm_mon % 10,
                 (date.tm_year - 2000) // 10,
                 (date.tm_year - 2000) % 10,
                 8,
                 8,
                 ])
            
    def buttons(self):
        """button events
        """
        def debounce_mode(pin, level, tick):
            self._mode_cb.cancel()
            self._event.send(self._mode_event)
            Timer(self._DEBOUNCE_DELAY,
                  lambda: self._gpio.callback(Ncs31x.MODE_BUTTON_PIN, self._INT_EDGE_RISING, debounce_mode),
                  []).start()

        def debounce_up(pin, level, tick):
            self._up_cb.cancel()
            self._event.send(self._up_event)
            Timer(self._DEBOUNCE_DELAY,
                  lambda: self._gpio.callback(Ncs31x.UP_BUTTON_PIN, self._INT_EDGE_RISING, debounce_up),
                  []).start()

        def debounce_down(pin, level, tick):
            self._down_cb.cancel()
            self._event.send(self._down_event)
            Timer(self._DEBOUNCE_DELAY,
                  lambda: self._gpio.callback(Ncs31x.DOWN_BUTTON_PIN, self._INT_EDGE_RISING, debounce_down),
                  []).start()

        self._ncs31x.init_pin(Ncs31x.UP_BUTTON_PIN)
        self._ncs31x.init_pin(Ncs31x.DOWN_BUTTON_PIN)
        self._ncs31x.init_pin(Ncs31x.MODE_BUTTON_PIN)

        self._mode_cb = self._gpio.callback(Ncs31x.MODE_BUTTON_PIN, self._INT_EDGE_RISING,
                                       debounce_mode)
        self._up_cb = self._gpio.callback(Ncs31x.UP_BUTTON_PIN, self._INT_EDGE_RISING,
                                     debounce_up)
        self._down_cb = self._gpio.callback(Ncs31x.DOWN_BUTTON_PIN, self._INT_EDGE_RISING,
                                     debounce_down)

    def __init__(self, conf_dict, event):
        """initialize the gra-afch module

            read the config file
            connect to the board
            blank the display and clear it
            set up button events
        """

        self._conf_dict = conf_dict;
        
        self._ncs31x = Ncs31x()
        self._gpio = self._ncs31x._gpio
        self._event = event
        self._dots = conf_dict["dots"]

        self._mode_event = event.event("mode-button", "down")
        self._up_event = event.event("up-button", "down")
        self._down_event = event.event("down-button", "down")
        
        self._ncs31x.blank()
        self._ncs31x.clear()

        self.buttons()
