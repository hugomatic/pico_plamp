import serial
import time
import argparse
import datetime

default_ser = None

def to_secs(hours, minutes=0, seconds=0):
    return seconds + minutes * 60 + hours * 60 * 60

def _send_command(ser_con, command):
    global default_ser

    ser = ser_con if ser_con is not None else default_ser

    ser.write( f'{command}\r\n'.encode())
    time.sleep(0.1)
    response = []
    while ser.in_waiting:
        response.append(ser.readline().decode().strip())
    return response

def set_time(time_override=None, ser=None):
    if time_override is None:
        # current_time = int(time.time()) % 86400
        # Get the current local datetime
        now = datetime.datetime.now()
        # Calculate seconds from midnight
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_from_midnight = int((now - midnight).total_seconds())
        hours = seconds_from_midnight / 60 / 60
        print(f"{now} seconds from midnight: {seconds_from_midnight} ({hours:.2f} h)")
        current_time = seconds_from_midnight
    else:
        current_time = time_override
    _send_command(ser, f"time {current_time}")
    return current_time

def set_light(start, duration, ser=None):
    _send_command(ser, f"light {start} {duration}")

def set_pump(on_interval, off_interval, ser=None):
    _send_command(ser, f"pump {on_interval} {off_interval}")

def get_menu(ser=None):
    responses = _send_command(ser, "a")
    return "".join(responses)

def get_state(ser=None):
    responses = _send_command(ser, "a")
    info = {}
    try:
        for l in responses[1:]:
            k,v = l.split(':')
            info[k.replace(' ', '_')] = v.strip()
        return info
    except Exception as e:
        print(f'Error processing info response: {e}')
        return None


def connect(serial_port='/dev/ttyACM0', baud=9600, timeout=1):
    global default_ser
    ser = serial.Serial(serial_port, baud, timeout=timeout)
    default_ser = ser
    return ser

def main(serial_port, update_time=False):
    with connect(serial_port) as ser:
        print(f"Connected to {serial_port}:")
        if update_time:
            print("Updating pico plamp time")
            set_time()
        print(f"Getting current state:")
        state = get_state(ser)
        try:
            for i,k in enumerate(state):
                v = state[k]
                print(f' {i:3} {k}: {v} ')
        except:
            print(f'{state=}')
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control a hydroponic system using a Raspberry Pi Pico.')
    parser.add_argument('--serial_port', type=str, default='/dev/ttyACM0',
                        help='The serial port to use for communication with the Pico.')
    # Add the optional --update-time argument
    parser.add_argument('-u', '--update-time', action='store_true',
                    help='Synchronizes the pico plamp time to the time of the host computer.')

    args = parser.parse_args()
    main(args.serial_port, args.update_time)

