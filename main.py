import evdev
import select
import urllib
import urllib.request
from urllib.error import URLError, HTTPError

class State:
    level:int = 0
    is_on: bool = False

    def __init__(self, level, is_on):
        self.level = level
        self.is_on = is_on

    def __str__(self):
        return f'{{level: {self.level}, is_on: {self.is_on}}}'

colours = ['red', 'green', 'blue', 'white', 'all']
levels = {}
active = 'white'

def do_network(method, action, colour, value=None):
    #path = 'http://10.0.0.203/api/v1/led/duty?name='
    #path = 'http://10.0.0.203/api/v1/led/on?name='
    #path = 'http://10.0.0.203/api/v1/led/off?name='
    if action not in ['duty', 'on', 'off']:
        raise Exception("BAD ACTION")
    if method == 'PUT' and value is None and action in ['duty']:
        raise Exception("BAD VALUE")
    path = f'http://10.0.0.203/api/v1/led/{action}?name={colour}'
    if method == 'PUT' and value is not None:
        path += f'&value={value}'
    print('path', path, 'method', method, 'value', value)
    req = urllib.request.Request(path, data=b'', method=method)
    try:
        res = urllib.request.urlopen(req, timeout=1)
        return res.read()
    except URLError:
        print("TIMEOUT")
        pass
    return None

def put(action, colour, value=None):
    return do_network('PUT', action, colour, value) == b'OK'

def get(action, colour):
    return do_network('GET', action, colour)

# bootstrap values
for c in colours:
    duty = int(get('duty', c))
    is_on = int(get('on', c)) == 1
    levels[c] = State(duty, is_on)
    print('Colour: ', c, str(levels[c]))


def put_level(colour, level):
    if level > 255:
        level = 255
    if level < 0:
        level = 0
    if put('duty', colour, level):
        levels[colour].level = level

def put_switch(colour, on):
    if put('on' if on else 'off', colour):
        levels[colour].is_on = on
    else:
        print('put fialed')

def change(direction):
    def _c():
        global active
        put_level(active, levels[active].level + direction)
    return _c

def toggle():
    def _t():
        put_switch('all', not levels['all'].is_on)
    return _t

def toggle_active():
    def _t():
        global active
        put_switch(active, not levels[active].is_on)
    return _t

def set_level(level):
    def _post():
        global active
        put_level(active, level)
    return _post

def change_active(colour):
    def _f():
        global active
        active = colour
    return _f

codes_to_action = {
        'KEY_POWER': toggle(),
        'KEY_DOWN': change(-1),
        'KEY_UP': change(1),
        'KEY_0': set_level(0),
        'KEY_1': set_level(4),
        'KEY_2': set_level(8),
        'KEY_3': set_level(76),
        'KEY_4': set_level(122),
        'KEY_5': set_level(153),
        'KEY_6': set_level(178),
        'KEY_7': set_level(198),
        'KEY_8': set_level(230),
        'KEY_9': set_level(255),
        'KEY_RED': change_active('red'),
        'KEY_GREEN': change_active('green'),
        'KEY_BLUE': change_active('blue'),
        'KEY_YELLOW': change_active('white'),
        'KEY_OK': toggle_active(),
}

device = evdev.InputDevice('/dev/input/by-path/platform-1f02000.ir-event')
print(device)
for event in device.read_loop():
    if event.type != evdev.ecodes.EV_KEY:
        continue
    key = evdev.categorize(event)
    if key.keystate != key.key_down:
        continue
    codes_to_action[key.keycode]()
