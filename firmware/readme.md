![firmware](../images/firmware.webp)

## prepare the pico for micro python

wget https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2

Ensure your user has permission to access the USB device.
You might need to add your user to the dialout group.

## use rshell to upload the


pip install rshell

The commands to send main.py to the pico should look like this

```
rshell -p /dev/ttyACM0
cp main.py /pyboard/
```

use make.bash to do it in 1 command
