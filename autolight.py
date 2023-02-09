from suncalcPy2 import getTimes
from datetime import datetime
from state import LightController


class AutoLight:
    lon = 19.4723
    lat = 50.2677

    def __init__(self, controlled: LightController):
        self.control = controlled

    def tick(self, date=None):
        self.control.fetch()
        white_led = self.control.colours['white']
        if not white_led.is_on:
            return

        date = date or datetime.now()
        times = getTimes(date, self.lon, self.lat)
        dusk = datetime.fromisoformat(times['dusk'])
        night = datetime.fromisoformat(times['night'])

        light = 0
        if dusk > date:
            print("before dusk")
        else:
            if night < date:
                print('full night')
                light = 1
            else:
                after_dusk = (date - dusk).total_seconds()
                dusk_night = (night - dusk).total_seconds()
                light = after_dusk / dusk_night

        max_light = 64
        light = light * light * max_light
        print("AUTOLIGHT:", light)
        white_led.set_level(light)
