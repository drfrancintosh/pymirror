# pymirror

- A MagicMirror clone written in Python
- Developed for low-resource RPI Zero 2 W
- Writes directly to the framebuffer using pygame

## Installation

- RPI OS Lite 32-bit
sudo apt update
sudo apt install git
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

## setup config.txt
- sudo vi /boot/firmware/config.txt
```
framebuffer_width=1280
framebuffer_height=720
framebuffer_depth=32
hdmi_force_hotplug=1
hdmi_group=1        # 1 = CEA (TV), 2 = DMT (computer monitor)
hdmi_mode=16        # 16 = 1080p @ 60Hz (use a suitable mode for your display)
```

## Running
- cd ~/pymirror
- python3 pymirror.py ## note: from the main console. The frame buffer is otherwise not available

