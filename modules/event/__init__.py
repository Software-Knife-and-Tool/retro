##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## events
##
##########

"""Manage retro events

Classes:
    Event

Functions:

    event(type_, arg)
    wait()
    send(ev)

Misc variables:

    VERSION

"""

import json
import sys
import os

from threading import Thread, Lock, Condition
from time import localtime, strftime, time, sleep
from datetime import datetime

##########
#
# event format:
#
# { "event" : arg }
#
# event:  button, alarm, ui-control
# arg:    context-based
#
# sneak in a timestamp somehow?
#

class Event:
    """the event class
    """

    VERSION = '0.0.3'

    _conf_dict = None

    _queue = None
    _queue_lock = None
    _queue_cv = None

    def wait(self):
        """grab an event from the event queue
        """

        with self._queue_cv:
            self._queue_cv.wait_for(lambda: len(self._queue))
            return self._queue.pop()
                
    def send(self, ev):
        """push an event on the event queue
        """

        with self._queue_cv:
            self._queue.append(ev)
            self._queue_cv.notify()

    def event(self, type_, arg):
        """create json event
        """

        fmt = '{{ "{}": "{}" }}'

        # print('event: ', end='')
        # print(fmt.format(type_, arg))
        # print(datetime.now().strftime('%H:%M:%S:%f'))

        return json.loads(fmt.format(type_, arg))

    def __init__(self):
        """create an event object
        """

        self._conf_dict = []
        with open(os.path.join(os.path.dirname(__file__), 'conf.json'), 'r') as file:
            self._conf_dict = json.load(file)

        self._queue_lock = Lock()
        self._queue_cv = Condition(self._queue_lock)
        self._queue = []
