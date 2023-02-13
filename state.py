import urllib.request
from urllib.error import URLError, HTTPError
from socket import timeout


class State:
    level: int = 0
    is_on: bool = False
    colour: str = ''

    def __init__(self, parent, colour, level=0, is_on=0):
        self.level = level
        self.is_on = is_on
        self.colour = colour
        self._parent = parent


    def __str__(self):
        return f'{{level: {self.level}, is_on: {self.is_on}}}'

    def fetch(self):
        self.level = self._get_duty()
        self.is_on = self._get_on()

    def toggle(self):
        if not self._parent._put('off' if self.is_on else 'on', self.colour):
            return False

        self.is_on = not self.is_on
        return True

    def set_level(self, level):
        level = max(min(level, 255), 0)

        if not self._parent._duty(self.colour, level):
            return False

        self.level = level
        return True

    def change(self, delta):
        return self.set_level(self.level + delta)

    def _get_duty(self):
        return self._parent._duty(self.colour)

    def _get_on(self):
        return self._parent._on(self.colour)

class LightController:
    timeout = 1
    timeout_tries = 10
    max_duty = 256
    debug: bool = True

    def __init__(self) -> None:
        self.states = [
            State(self, 'red'), State(self, 'green'), State(self, 'blue'),
            State(self, 'white'), State(self, 'all'),
        ]
        self.colours = {x.colour: x for x in self.states}
        self._active = self.colours['white']

    def fetch(self):
        res = urllib.request.urlopen('http://10.0.0.203/api/v1/pwm/range')
        self.max_duty = int(res.read())
        for s in self.states:
            s.fetch()

    def set_active(self, colour):
        self._active = self.colours[colour]

    @property
    def active(self):
        return self._active

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

    def _duty(self, colour, value=None):
        if value:
            value *= self.max_duty / 255
            value = int(value)
        ret = int(self._get_or_put('duty', colour, value))
        if not value:
            ret *= (255 / self.max_duty)
        return int(ret)

    def _on(self, colour, value=None):
        return int(self._get_or_put('on', colour, value)) == 1

    def _off(self, colour, value=None):
        return int(self._get_or_put('off', colour, value)) == 1

    def _get_or_put(self, action, colour, value=None):
        if value is None:
            return self._get(action, colour)
        return self._put(action, colour, value)

    def _put(self, action, colour, value):
        return self._do_network('PUT', action, colour, value) == b'OK'

    def _get(self, action, colour):
        return self._do_network('GET', action, colour)
