import json
import os
import time
from datetime import datetime
from subprocess import call

def read_config():
    with open('plamp_service_config.json', 'r') as file:
        return json.load(file)

def take_picture(picture_directory):
    seconds_since_midnight = int((datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
    timestamp = datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
    filename = f"{seconds_since_midnight}_{timestamp}.png"
    filepath = os.path.join(picture_directory, filename)
    call(['rpicam-jpeg', '-o', filepath])
    print(f"Picture saved: {filepath}")

def main():
    config = read_config()
    interval_seconds = config.get('interval_seconds', 300)  # Default interval
    picture_directory = config.get('picture_directory', '/path/to/default/directory')  # Default directory

    while True:
        take_picture(picture_directory)
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()

