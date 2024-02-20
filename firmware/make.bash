#!/bin/bash

# Path to your main.py file
MAIN_PY_PATH="./main.py"

# Path to the Pico's device, change this if needed
PICO_DEVICE="/dev/ttyACM0"

# Check if main.py exists
if [ ! -f "$MAIN_PY_PATH" ]; then
    echo "Error: main.py not found at $MAIN_PY_PATH"
    exit 1
fi

# Check if the Pico device exists
if [ ! -e "$PICO_DEVICE" ]; then
    echo "Error: Pico device not found at $PICO_DEVICE"
    exit 1
fi


# Upload main.py to Pico using rshell
echo "Uploading main.py to Pico..."
rshell -p $PICO_DEVICE << EOF
cp $MAIN_PY_PATH /pyboard/
EOF

echo "Upload complete."

