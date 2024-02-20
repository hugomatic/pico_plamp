from machine import Pin, Timer
import time
import json

# Defaults settings
class Settings:
    light_start_time = 21600 # 6am
    light_on_interval = 36000  # 10 hours
    pump_on_interval = 900  # 15 minutes
    pump_off_interval = 900  # 15 minutes
    current_time = 0

    def to_dict(self):
        return  {
            'light_start_time': self.light_start_time,
            'light_on_interval': self.light_on_interval,
            'pump_on_interval': self.pump_on_interval,
            'pump_off_interval': self.pump_off_interval,
            'current_time': self.current_time
        }

    def load_dict(self, data):
        for key, value in data.items():
             setattr(self, key, value)

class Board:
    # Pin numbers
    light_pin_nb = 2
    pump_pin_nb = 3
    # where state is saved
    file_path = 'state.json'

    def __init__(self):
      # Initialize GPIO pins
      self.light_relay = Pin(self.light_pin_nb, Pin.OUT)
      self.pump_relay = Pin(self.pump_pin_nb, Pin.OUT)
      self.led = machine.Pin(25, machine.Pin.OUT)

    def save_settings(self):
        global settings
        data = settings.to_dict()
        with open(self.file_path, 'w') as file:
            json.dump(data, file)

    def load_settings(self):
        global settings
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                settings.load_dict(data)
        except Exception as e:
            print(f'Error reading {self.file_path}: {e}')

    def blink(self, nb, delay=0.1):
        for i in range(nb):
            self.led.value(1)
            time.sleep(delay)
            self.led.value(0)
            time.sleep(delay)


# keeping state
class State:
    light = False
    pump = False
    light_on_elapsed = 0
    light_off_elapsed = 0
    pump_on_elapsed = 0
    pump_off_elapsed = 0


# Timer callback
def timer_callback(timer=None):
    global board, settings, state

    settings.current_time += 1

    light = duration_timer_status(settings.light_start_time,
                                  settings.light_on_interval,
                                  settings.current_time)
    state.light, state.light_on_elapsed, state.light_off_elapsed = light

    pump = periodic_timer_status(settings.pump_on_interval,
                                 settings.pump_off_interval,
                                 settings.current_time)
    state.pump, state.pump_on_elapsed, state.pump_off_elapsed = pump

    # update relays
    board.light_relay.value(state.light)
    board.pump_relay.value(state.pump)

    # save every 5 minute (so that systems keeps us with short power outages)
    if settings.current_time % 300 == 0:
        board.save_settings()


def duration_timer_status(start_time, duration, current_time):
    """
    Determine the status of a timer given the start time, duration, and the current time.
    Simplified approach using normalized time.

    :param start_time: Start time of the timer in seconds (0 to 86400).
    :param duration: Duration of the timer in seconds (0 to 86400).
    :param current_time: Current time in seconds since midnight (0 to 86400).
    :return: Tuple with the timer status (bool), on elapsed, off elapsed
    """
    on_time = duration
    off_time = 86400 - duration
    norm_time = (current_time - start_time) % (on_time + off_time)

    if norm_time < on_time:
        status = True  # Timer is ON
        state_length = on_time
        on_elapsed = norm_time
        off_elapsed = 0
    else:
        status = False  # Timer is OFF
        state_length = off_time
        on_elapsed = 0
        off_elapsed = norm_time - on_time
    return status, on_elapsed, off_elapsed


def periodic_timer_status(on_interval, off_interval, current_time):
    """
    Determine the status of a timer given on off intervals.
    starts at time 0 (midnight) in ON state
    """
    # normalize current time to the interval that starts at 0
    norm_time = current_time  % (on_interval + off_interval)
    status = norm_time < on_interval
    if status:
        on_elapsed = norm_time
        off_elapsed = 0
    else:
        on_elapsed = 0
        off_elapsed = norm_time - on_interval
    return status, on_elapsed, off_elapsed


# init data
settings = Settings()
state = State()
# Read the current data
board = Board()
board.load_settings()
board.blink(3)
# Set up the timer
timer = Timer()
timer.init(freq=1, mode=Timer.PERIODIC, callback=timer_callback)

# Main loop to listen for and process incoming commands
while True:
    cmd = input().strip().lower()
    if cmd == "?":
        print("Available commands:")
        print('')
        print("time <current_time>")
        print("light <light_start_time> <light_duration>")
        print("pump <pump_on_interval> <pump_off_interval>")
        print("[c]config")
        print("sett[i]ngs")
        print("[s]tate")
        print("[a]ll")

    elif cmd.startswith("time"):
        _, new_time = cmd.split()
        settings.current_time = int(new_time)
        board.save_settings()

    elif cmd.startswith("light"):
        _, start, duration = cmd.split()
        settings.light_start_time = int(start)
        settings.light_on_interval = int(duration)
        board.save_settings()

    elif cmd.startswith("pump"):
        _, on_interval, off_interval = cmd.split()
        settings.pump_on_interval = int(on_interval)
        settings.pump_off_interval = int(off_interval)
        board.save_settings()

    elif cmd in  ["c", "i", "s", "a", "config", "settings", "state", "all"]:
        # config
        if cmd in ["c", "a", "config", "all"]:
            print(f"units: seconds")
            print(f"light pin: {board.light_pin_nb}")
            print(f"pump pin: {board.pump_pin_nb}")
        # settings
        if cmd in ["i", "a", "settings", "all"]:
            print(f"current time: {settings.current_time}")
            print(f"light start time: {settings.light_start_time}")
            print(f"light on interval: {settings.light_on_interval}")
            light_off_interval = 86400 - settings.light_on_interval
            print(f"light off interval: {light_off_interval}")
            print(f"pump on interval: {settings.pump_on_interval}")
            print(f"pump off interval: {settings.pump_off_interval}")
        # state
        if cmd in ["s", "a", "state", "all"]:
            print(f"light: {state.light}")
            print(f"light on elapsed: {state.light_on_elapsed}")
            print(f"light off elapsed: {state.light_off_elapsed}")
            print(f"pump: {state.pump}")
            print(f"pump on elapsed: {state.pump_on_elapsed}")
            print(f"pump off elapsed: {state.pump_off_elapsed}")
        board.blink(2)
    else:
        print(f'unknown cmd: {cmd}')
        board.blink(5)
