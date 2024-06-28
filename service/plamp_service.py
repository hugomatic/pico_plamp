import json
import os
import time
from datetime import datetime
from subprocess import call

def read_config():
    with open('plamp_service_config.json', 'r') as file:
        return json.load(file)

def take_picture(picture_directory):
    seconds_since_midnight = int(time.time())
    timestamp = datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
    filename = f"{seconds_since_midnight}_{timestamp}.jpg"
    filepath = os.path.join(picture_directory, filename)
    captured = False
    try:
        x = call(['libcamera-jpeg', '-o', filepath])
        captured = True
    except Exception as e:
        print('error {e}')
    if not captured:
        try:
            call(['rpicam-jpeg', '-o', filepath])
            captured = True
        except:
            print('error {e}')
    if captured:
        print(f"Picture saved: {filepath}")
    else:
        print(f"Can't capture image!")
def main():
    config = read_config()
    interval_seconds = config.get('interval_seconds', 300)  # Default interval
    picture_directory = config.get('picture_directory', '/path/to/default/directory')  # Default directory

    while True:
        take_picture(picture_directory)
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()

