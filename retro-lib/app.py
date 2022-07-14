import time
import os
import json

from bottle import template, route, run, static_file
from threading import Thread

from retro import Retro
from event import Event

import jyserver.Bottle as js
@js.use
class App():
    start0 = None
    
    def version(self):
        self.js.document.GetElementById('version').innterHTML = '0.0.1'

    @js.task
    def main(self):
        self.start0 = time.time()
        while True:
            t = "{:.1f}".format(time.time() - self.start0)
            self.js.document.GetElementById('system-time').innterHTML = t
            time.sleep(0.1)

@route('/')
def static():
    # App.main()
    # return App.render(file='static/html/index.html')
    return static_file('html/index.html', root='/home/putnamjm/retro/static', mimetype='text/html')

@route('/<dir>/<file>')
def static(dir, file):
    return static_file(os.path.join(dir, file), root='/home/putnamjm/retro/static')

@route('/static/<dir>/<file>')
def static(dir, file):
    return static_file(os.path.join(dir, file), root='/home/putnamjm/retro/static')

conf_dict = []
with open(os.path.join(os.path.dirname(__file__), '../etc/retro.json'), 'r') as file:
    conf_dict = json.load(file)

retro = Retro(conf_dict)
    
event_thread = Thread(group=None, target=retro.display.event_loop, name=None, args=(), kwargs={})

# inhale deeply
time.sleep(4)
retro.display.unblank_display()

event_thread.start()

run(host='moderne', port=8080, debug=True)
