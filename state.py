import urllib.request
from urllib.error import URLError, HTTPError

def do_network(method, action, colour, value=None):
    if action not in ['duty', 'on', 'off']:
        raise Exception("BAD ACTION")
    if method == 'PUT' and value is None and action in ['duty']:
        raise Exception("BAD VALUE")
    path = f'http://10.0.0.203/api/v1/led/{action}?name={colour}'
    if method == 'PUT' and value is not None:
        path += f'&value={value}'
    # print('path', path, 'method', method, 'value', value)
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

class State:
    level:int = 0
    is_on: bool = False
    colour: str = ''

    def __init__(self, colour, level=0, is_on=0):
        self.level = level
        self.is_on = is_on
        self.colour = colour

    def __str__(self):
        return f'{{level: {self.level}, is_on: {self.is_on}}}'

    def fetch(self):
        self.level = int(get('duty', self.colour))
        self.is_on = int(get('on', self.colour)) == 1

    def toggle(self):
        if not put('off' if self.is_on else 'on', self.colour):
            return False

        self.is_on = not self.is_on
        return True

    def set_level(self, level):
        level = max(min(level, 255), 0)

        if not put('duty', self.colour, level):
            return False

        self.level = level
        return True

    def change(self, delta):
        return self.set_level(self.level + delta)


class LightController:
    states = [
        State('red'), State('green'), State('blue'),
        State('white'), State('all'),
    ]
    colours = {x.colour: x for x in states}
    _active = colours['white']

    def __init__(self) -> None:
        pass

    def fetch(self):
        for s in self.states:
            s.fetch()

    def set_active(self, colour):
        self._active = self.colours[colour]

    @property
    def active(self):
        return self._active
