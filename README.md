# pymirror

- A Python Dashboard inspired by Magic Mirror 2 
    - By Greg Smith (greg@agilefrontiers.com)
    - Created June, 2025
- Developed for low-resource RPI Zero 2 W
- Writes directly to the frame buffer using Pillow / PIL

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

- Install with `pip install -r requirements.txt`
- or `sudo apt-get install python3-<module>` (for RPI)
    - python-dotenv
    - Pillow
    - jinja2
    - flask
    - requests
    - numpy

## setup config.txt
- sudo vi /boot/firmware/config.txt

```ini
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
- The Default font DejaVuSerif.ttf was delivered with RPI-OS and copied locally for convenience
- Update `fontlist.txt` as per your system

## Running
- `cd ~/git/pymirror`
- `./run.sh`

## Web Server

- GET: `http://rp01.local:8080`
    - serves up HTML pages that allow you to control your PyMirror
- POST: `http://rpi01.local:8080/command`
    - will allow you to publish an `event` directly to PyMirror
    - All "subscribed" modules will receive the event 
    - the payload is event-specific...
    - Here is an example for the `alert` module
```json
{
    "name": "weather_alert",
    "heading": "Hello PyMirror!",
    "body": "This is your first PyMirror event",
    "footer": "(C) 2025",
    "timeout": 10000
}
```

## Folders

- configs - individual .json config files
- events - python classes for each type of event that can be published
- fonts - local font.ttf files
- modules - python classes implementing each module
- pmsever - the flask web server class and other files (html, etc...)
- pymirror - pymirror python source files
- random - test code and other fancy bicuits

## Files

- .env - list of environment variables in KEY=value format (ignored by .gitignore, read into the PyMirror os.environ)
- .secrets - list of API keys in KEY=value format (ignored by .gitignore, read into the PyMirror os.environ)
- config.json - PyMirror main config file
- fontlist.txt - PyMirror list of fonts and where to find them
- output.jpg - optional dump of the framebuffer for debugging
- preview.html - test HTML to display output.jpg in browser
- preview.sh - script to display preview.html / output.jpg in browser
- README.md - this file
- requirements.txt - list of Python packages needed to support PyMirror and the default modules
- run.sh - script to run PyMirror
- test.py - random Python test script for debugging
- test1.sh - random shell test script for debugging
- TODO.md - wish list of things to add to PyMirror

## Modules

- Modules are stored in the `./modules` folder
- The name of the module must be the snake-case version of the camel-case name of the module class
- In the `config.json` you can call up a module multiple times with differet instances

## config.json

```json
{
  "debug": false, // debug will write a white border around each module and print its name in the upper left corner
  "secrets": ".secrets", // the location of your secrets file which holds API keys
  "screen": { // definition of the screen you're displaying on
    "output_file": "output.jpg", // optional output JPEG of the screen updated on each flush() for debugging
    "frame_buffer": null, // the frame buffer on the rpi to write to. usually /dev/fb0 (mau be null if you are debugging)
    "font": "DejaVuSans.ttf", // the default system font face (see fontlst.txt)
    "font_size": 64, // the default font size
    "color": "(255,255,255)", // default graphics color [colors are either tuples or HTML hex codes]
    "bg_color": "#000000", // default background color
    "text_color": "(255,255,255)", // the default text color
    "text_bg_color": null, // the default text background color (null == transparent)
    "width": 1920, // display width in pixels
    "height": 1080, // display height in pixels
    "rotate": 0 // rotation for portrait [0, 90, 180, 270]
  },
  "positions": { // the list of possible module positions on the screen, expressed as a percentage of the screen
    "None": "0.0,0.0,0.0,0.0", // special case for modules that don't have a positing (cron, eg)
    "top_left": "0.0,0.15,0.33,0.33", // you can make up any names you like.
    "top_center": "0.00,0.0,1.0,0.15", // coords are fractions 0.0-1.0 as "x0,y0,x1,y1"
    "top_right": "0.66,0.15,1.00,0.33", // you can have as many of these as you like and they may overlap if you like
    "middle_left": "0.0,0.33,0.33,0.66",
    "middle_center": "0.33,0.15,0.66,0.85",
    "middle_right": "0.7,0.33,1.00,0.66",
    "bottom_left": "0.0,0.66,0.33,1.00",
    "bottom_center": "0.33,0.85,0.66,1.00",
    "bottom_right": "0.66,0.66,1.00,1.00"
  },
  "modules": [ // list of module config files
    "configs/fps.json", // note that you can also insert the module config directly here
    "configs/weather_alert.json", // but that is unweildy
    "configs/weather.json", // a single .json per module is easier to manage
    "configs/fortune.json",
    "configs/web_api.json",
    "configs/date.json",
    "configs/time.json",
    "configs/analog_clock.json",
    "configs/day_of_week.json"
  ]
}
```

## Module Config Files (./configs)

```json
{
    "module": "analog_clock", // the name of the module file stored in ./modules
    "moddef": { // module definitions shared by all modules
        "name": "analog_clock", // a name that identifies this instance of the module (you can have multiple instances of the same module)
        "color": "#c0c000", // if specified, overrides the screen's default gfx color
        "bg_color": "#000000", // if specified, overrides the screen's default bgnd color
        "text_color": "#c0c000", // if specified, overrides the screen's default text color
        "text_bg_color": "#000000", // if specified, overrides the screen's default text_bgnd color
        "position": "middle_center", // the position on the screen - see "config.json/positions" above
        "font": "TOS_Title.ttf", // the default font, overrides the screen's default font name (see fontlist.txt)
        "font_size": 48 // the default font_size, overrides the screen's default font dize (see fontlist.txt)
    },
    "config": { // configurations specific to this module... could be anything. see specific module docs
        "hour_hand": "#ff0000",
        "minute_hand": "#00ff00",
        "second_hand": "#2020ff"
    }
}
```