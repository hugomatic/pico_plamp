#!/bin/bash

# List of commands - add new commands here
commands=(
    "sudo systemctl status plamp_service"
    "sudo systemctl start plamp_service"
    "sudo systemctl stop plamp_service"
    "libcamera-jpeg -o test.png"
    "sudo apt-get install libraspberrypi-bin nmap"
    "pip install -r requirements.txt"
    "nmap -p 22 --open 192.168.1.0/24"
)

# Display the command menu
show_menu() {
    echo "Select a command to run:"
    for i in ${!commands[@]}; do
        echo "$((i+1))) ${commands[$i]}"
    done
}

# Execute the selected command
run_command() {
    if [[ $1 -le ${#commands[@]} ]]; then
        eval "${commands[$(($1 - 1))]}"
    else
        echo "Invalid option."
    fi
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (or 'q' to quit): " choice

    if [[ "$choice" = "q" ]]; then
        break
    elif [[ "$choice" =~ ^[0-9]+$ ]]; then
        run_command $choice
    else
        echo "Invalid input."
    fi
    echo
done

echo "Script exited."

