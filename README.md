# pymirror

- A MagicMirror clone written in Python
- Developed for low-resource RPI Zero 2 W
- Writes directly to the framebuffer using pygame

## Installation

- RPI OS Lite 32-bit
- sudo apt update
- sudo apt install git
- add ssh private key to .ssh
- eval "$(ssh-agent -s)"
- ssh-add ~/.ssh/id_rsa
- ssh -T git@github.com
- git clone git@github.com:devcybiko/pymirror.git

## Installing Libraries
- sudo apt-get update
- sudo apt-get install python3-pygame
- sudo apt-get install python3-pip
- sudo apt-get install python3-venv
- sudo apt-get update
- sudo apt-get install libsdl2-2.0-0
- sudo apt-get install libsdl2-dev
- sudo apt-get install libfreetype6 libfreetype6-dev
- sudo apt-get install fbi fbset
- sudo usermod -aG video $USER

## installing PIL
sudo apt install python3-pillow

## setup config.txt
- sudo vi /boot/firmware/config.txt
```
[all]
framebuffer_width=1920
framebuffer_height=1080
framebuffer_depth=32
hdmi_ignore_edid=1
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=16
# Set rotation if needed (0 = no rotation, 1 = 90 degrees, etc.)
display_rotate=0    # Set rotation if needed (0 = no rotation, 1 = 90 degrees, etc.)
```
## Fontlist.txt

- One font per line
- Basically the output of "fc-list"
- add your own fonts as well
- The fonts in the `fonts` folder were appropriated from https://www.st-minutiae.com/resources/fonts/index.html
- There were no credits there, but if anyone knows who to credit, I'll add credits here
- The 7segment.txt font was from https://torinak.com/font/7-segment
- The Default 
## Running
- cd ~/pymirror
- python3 pymirror.py ## note: from the main console. The frame buffer is otherwise not available

