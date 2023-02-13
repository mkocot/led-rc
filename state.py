import urllib.request
from urllib.error import URLError, HTTPError
from socket import timeout


class State:
    timeout = 1
    timeout_tries = 10
    level: int = 0
    is_on: bool = False
    colour: str = ''
    debug: bool = True

    def __init__(self, colour, level=0, is_on=0):
        self.level = level
        self.is_on = is_on
        self.colour = colour

    def _do_network(self, method, action, colour, value=None):
        if action not in ['duty', 'on', 'off']:
            raise Exception("BAD ACTION")
        if method == 'PUT' and value is None and action in ['duty']:
            raise Exception("BAD VALUE")
        path = f'http://10.0.0.203/api/v1/led/{action}?name={colour}'
        if method == 'PUT' and value is not None:
            path += f'&value={value}'

        if self.debug:
            print(f'{method} {path}')

        # just try few times and bail
        for _ in range(self.timeout_tries):
            req = urllib.request.Request(path, data=b'', method=method)
            try:
                res = urllib.request.urlopen(req, timeout=self.timeout)
                return res.read()
            except timeout:
                print("SOCKET timeout", path)
                continue
            except URLError:
                print("TIMEOUT", path)
                continue
        return None

    def _put(self, action, colour, value=None):
        return self._do_network('PUT', action, colour, value) == b'OK'

    def _get(self, action, colour):
        return self._do_network('GET', action, colour)

    def __str__(self):
        return f'{{level: {self.level}, is_on: {self.is_on}}}'

    def fetch(self):
        self.level = int(self._get('duty', self.colour))
        self.is_on = int(self._get('on', self.colour)) == 1

    def toggle(self):
        if not self._put('off' if self.is_on else 'on', self.colour):
            return False

        self.is_on = not self.is_on
        return True

    def set_level(self, level):
        level = max(min(level, 255), 0)

        if not self._put('duty', self.colour, level):
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
