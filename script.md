# Intro

- I had a Magic Mirror project on my wall a few years back.
- It was based on a Raspberry Pi Zero 1.1 
- I removed it when I needed it for another project.

- A couple weeks ago I decided I wanted a clock on the wall and thought a Magic Mirror would be a better solution.
- I had about 16 surplus monitors at my disposal
- Perhaps I could adorn my wall with 4 of these?

- But when I tried to resurrect my project I found that Magic Mirror had grown too large to run on a RPI Zero - even in a Headless mode.
- So I decided to try building a Python version of Magic Mirror that would write directly to the frame buffer.
- The result not only worked well, but well beyond my expectations.
- This one's going to get technical fast - so buckle up, buckaroos!
- Introducing PyMirror - right after this... 
- On Dr. Francintosh

# Demo
1. Clock Module 
  * Time
  * Date
  * Day of Week
  * Week of Month
2. Analog Clock
3. Weather
4. News
5. Fortune
6. Alert / Weather Alert
7. FPS
8. Web Interface
  * Send Alert
  * Debug
  * Logging
  * Remote Display
    * It's not really for web-based use
    * But is very handy for remote observation

## Design Goals

1. A close approximation to Magic Mirror
2. Operates on RPi Zero or Zero 2 W (low cost)
2. Direct Frame Buffer Access (No need for Desktop or Browser)
3. Modular - easy to add new features
2. Configurable via config.json
4. Fast enough to handle multiple modules at minimum 1-FPS
5. Duplicate MM Basic Modules
6. Internet ready
6. Optional: Web controllable

## Frame Buffer Access

* the RPi Zero has a memory-mapped Frame Buffer for the HDMI Display
* /dev/fb0
* It's configurable at the kernel level
* We'll focus on 1920 x 1080
* We get 16-bit 565-RGB
* Other configurations are possible, but not at this time
* In the future there may be "device drivers" for different display formats

## Graphics Package

* Several candidates
    * "Roll your own" 
        * Lots of work
        * Distraction from the goal
    * PyGame 
        * tried it and it no longer supports direct frame-buffer rendering
    * Pillow for RPi
        * this one met all my needs
* Allows bit mapped graphics rendering
* Rendering to a memory-allocated bitmap
* The direct copying to the /dev/fb0 frame buffer
* But - there is an "impedance mismatch"
* I can render 32-bit graphics using Pillow
  * But the Frame Buffer is 16-bits
  * I had to convert "RGB" colors to an internal format
  * Transforming and copying the in-memory Frame Buffer is slow in Python
  * Python is interpreted
  * So numpy is used since it's written in 'C' and callable from Python
* Eventually, each Module gets its own bit map (aids in "clipping")
* Rotation for Portrait mode is available

## config.json

* Allows configuration
* Specifies "positions"
  * Configurable (I don't know if MM2 offers this)
* Positions are defined by percentage of the total screen

## Modules

* Modules are defined in the `modules` folder as a Python file
* And extend the `PMModule` class
* Each module is configured in
  * config.json - like in MM2
  * or its own "moddef" json file
* must select a "Position" that is pre-defined in config.json
* must implement two main functions
    * `exec()` which updates the module's internal "state"
    * `render()` which draws the module's text and graphics on the display
* `exec()` returns True if the state has changed and False otherwise
* PyMirror will only call the module's `render()` method if `exec()` returns True
* This improves performance by only updating the screen when necessary

## Standard Module Classes

* PMModule - Base module class
* PMCard - Header, Footer, Body
* PMWebAPI - A module that makes requests of the internet
  * Includes Caching for when the internet is down
  * Or to prevent exceeding the API rate limit
  * By polling the local file copy of the payload rather than reaching out to the internet

## PyMirror Task Management

* The Main Loop
```python
while True:
    self._read_server_queue() # read any new events from the server queue
    self._send_all_events()  # send all new events to the modules
    modules_changed = self._exec_modules() # update / check the state of all modules
    self._render_modules(modules_changed)  # Render only the modules that changed state
    self._update_screen()  # Update the screen with the rendered modules
    time.sleep(0.01) # Sleep for a short time to give pmserver a chance to process web requests
```
* Cooperative Multi-tasking
* Each module is a task, and it must return control
* Python has only one "thread" - so each task must be frugal
* Internet calls are not asynchronous
  * So an Internet call could hang the display
  * This a future task

## Inter-task communication

* Pub/Sub interface
* Events are Python dictionaries
    * I wanted to limit events to subclasses of PMEvent
    * No time... Future task
* Modules can "subscribe" to an event type
* Modules can also "publish" events that are sent to any "listeners" or "subscribers"
* A Queue is used to gather events from the local area network
* Each event has an event 'name'
* All events are sent to the Module's `onEvent()` method
    * before `exec()` is called
* There is a `dispatch_method()` that will 
  * call the module's `onEventName()` method if it exists

## Future Work

* Magic Mirror Look / Feel
* Asynchronous Internet Calls
* PMEvent Class
* PMText class (blinking, fading, scrolling X/Y axis)
* PMScreen device drivers
* Calendar Module
* Security WebCam Module
* Photo Album Slideshow
* Weather Maps
* PyCamera support?

# Final thoughts & Comparison to Magic Mirror

* Colors are more garish - personal choice
    * Magic Mirror is for "up close and personal"
    * PyMirror is more of a Dash Board
    * But, should be configurable to look like Magic Mirror
* Slower, but needs fewer resources
    * runs easily on RPi Zero 1.1 and RPi 02w
    * could it run on RPi Pico? Probably!
    * use my Simple VGA/HDMI project
    * Plus MicroPython or Circuit Python
* Not Browser-based
    * Bit mapped graphics are simpler
    * But we lose many layout and animation features a browser-based solution gives us
* Simpler in approach
    * Might be easier to add new modules
    * No need to create CSS, HTML, JavaScript files
    * Python-based - easier or harder?
* Fewer Modules
    * No third party modules ... yet!
    * because it's so new
* Open Source and available in my GitHub
* Still a Work in Progress

## In Closing

* As always
* Please don't like this video
* Please don't subscribe to this channel
* Don't look at my other channels or click here or there.
* You're time is precious, so please don't waste it on anything I'm doing
* But... As always... 
* Thank you for spending part of your time here with me
* And I'll see you next time...
* On Dr. Francintosh