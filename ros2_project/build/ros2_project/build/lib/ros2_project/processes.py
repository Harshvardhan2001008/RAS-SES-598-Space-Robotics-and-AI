#!/usr/bin/env python3

import subprocess
import time

# List of commands to run
commands = [
    # Run the Micro XRCE-DDS Agent
    #"MicroXRCEAgent udp4 -p 8888",

    # Run the PX4 SITL simulation with proper world and spawn height
    "bash -c 'cd ~/PX4-Autopilot && export PX4_GZ_WORLD=custom_world && export PX4_GZ_MODEL_POSE=\"0 14.5 6.5 0 0 0\" && make px4_sitl gz_x500_depth; exec bash'",

    # Optional: Run QGroundControl
    # "bash -c 'cd ~/QGroundControl && ./QGroundControl.AppImage; exec bash'"
]

# Loop through each command in the list
for command in commands:
    subprocess.run(["gnome-terminal", "--tab", "--", "bash", "-c", command])
    time.sleep(1)

