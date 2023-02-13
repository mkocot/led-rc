from suncalcPy2 import getTimes
from datetime import datetime
from state import LightController


class AutoLight:
    lon = 19.4723
    lat = 50.2677
    max_light = 64

    def __init__(self, controlled: LightController):
        self.control = controlled

    def tick(self, date=None):
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

        light = int(light * light * self.max_light)

        white_led = self.control.colours['white']
        white_led.fetch()

        print(f'AUTOLIGHT: {light}, apply: {white_led.is_on}')

        if not white_led.is_on:
            return

        # Ignore if matches
        if white_led.level == light:
            return

        white_led.set_level(light)
