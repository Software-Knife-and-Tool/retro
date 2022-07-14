import time
import os
import json

from datetime import datetime

from bottle import template, route, run, static_file
from threading import Thread

from retro import Retro
from event import Event

import jyserver.Bottle as js

up_since = datetime.now()

conf_dict = []
with open(os.path.join(os.path.dirname(__file__), '../etc/retro.json'), 'r') as file:
    conf_dict = json.load(file)

retro = Retro(conf_dict)

event_thread = Thread(group=None, target=retro.display.event_loop, name=None, args=(), kwargs={})

@js.use
class App():
    @js.task
    def update_clock(self, retro):
        while True:
            self.js.dom.version.innerHTML = retro.version()
            self.js.dom.up_time.innerHTML = up_since.strftime('%m/%d/%Y %H:%M:%S')
            self.js.dom.display_time.innerHTML = retro.display.display_time().strftime('%m/%d/%Y %H:%M:%S')
            self.js.dom.system_time.innerHTML = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
            time.sleep(1)

@route('/')
def static():
    with open('/home/putnamjm/retro/static/html/index.html') as f: html = f.read()
    
    App.update_clock(retro)
    return App.render(html)
    # return static_file('html/index.html', root='/home/putnamjm/retro/static', mimetype='text/html')

@route('/<dir>/<file>')
def static(dir, file):
    return static_file(os.path.join(dir, file), root='/home/putnamjm/retro/static')

@route('/static/<dir>/<file>')
def static(dir, file):
    return static_file(os.path.join(dir, file), root='/home/putnamjm/retro/static')

# inhale deeply
time.sleep(4)
retro.display.unblank_display()

event_thread.start()

run(host='retro', port=8080, debug=True)
