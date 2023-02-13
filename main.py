import evdev
import asyncio
from state import LightController
from autolight import AutoLight
import time

controlled = LightController()
controlled.fetch()
controlled.set_active('white')

autolight = AutoLight(controlled)
auto_enabled = True

def disable_auto():
    global auto_enabled
    auto_enabled = False

def enable_auto():
    global auto_enabled
    auto_enabled = True
    white = controlled.colours['white']
    level = white.level
    for _ in range(2):
        white.set_level(0)
        time.sleep(0.2)
        white.set_level(32)
        time.sleep(0.2)
    white.set_level(level)
    autolight.tick()

def toggle_auto():
    def _f():
        global auto_enabled
        if auto_enabled:
            disable_auto()
        else:
            enable_auto()
    return _f

def change(direction):
    def _c():
        disable_auto()
        # don't go to 0
        if controlled.active.level + direction == 0:
            return
        controlled.active.change(direction)
    return _c


def toggle():
    def _t():
        disable_auto()
        controlled.colours['all'].toggle()
    return _t


def toggle_active():
    def _t():
        disable_auto()
        controlled.active.toggle()
    return _t


def set_level(level):
    def _post():
        disable_auto()
        controlled.active.set_level(level)
    return _post


def change_active(colour):
    def _f():
        disable_auto()
        controlled.set_active(colour)
    return _f


codes_to_action = {
    'KEY_POWER': toggle(),
    'KEY_DOWN': (change(-1), (evdev.KeyEvent.key_down, evdev.KeyEvent.key_hold)),
    'KEY_UP': (change(1), (evdev.KeyEvent.key_down, evdev.KeyEvent.key_hold)),
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
    'KEY_PLAY': toggle_auto(),
}


def ir_receiver():
    device = evdev.InputDevice('/dev/input/by-path/platform-1f02000.ir-event')
    print(device)

    for event in device.read_loop():
        if event.type != evdev.ecodes.EV_KEY:
            continue
        key = evdev.categorize(event)
        tuple_or_func = codes_to_action[key.keycode]
        if not isinstance(tuple_or_func, tuple):
            tuple_or_func = (tuple_or_func, (key.key_down,))
        func, keys = tuple_or_func
        if key.keystate not in keys:
            continue
        print("Handle KEY", key)
        func()


async def auto_light_adjust():
    global auto_enabled
    loop = asyncio.get_running_loop()
    while loop.is_running():
        if auto_enabled:
            autolight.tick()
        await asyncio.sleep(60)


async def main():
    auto_light_task = asyncio.create_task(auto_light_adjust())
    ir_receiver_task = asyncio.create_task(asyncio.to_thread(ir_receiver))
    done, pending = await asyncio.wait([auto_light_task, ir_receiver_task], return_when=asyncio.FIRST_COMPLETED)
    for p in pending:
        p.cancel()
        await p
    print("dang")


asyncio.run(main())
