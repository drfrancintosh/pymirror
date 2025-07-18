# TODO List

## MVP - before launch on Dr. Francintosh

## Other Notes

- add github ssh private key to .ssh
- eval "$(ssh-agent -s)"
- ssh-add ~/.ssh/id_rsa
- ssh -T git@github.com

## Special Commands
- vcgencmd get_throttled
- vcgencmd get_config int
- dmesg -w

## .bashrc
echo "PyMirror Started"
setterm -cursor off 
cd git/pymirror
./run.sh

## Backlog


8. if alert card is 'timed', show timer percent. bar

6. Hot Reload of config.json
    - if config.json is updated then dispose of old modules and reload

1. Error Handling
    1. weather.py - error checking for bad api results
    1. Better error handling

17. add device drivers for display

18. switch to JSON5 for easier JSON editing.

19. add color palette to config.json

20. Make Longer "card body" text scroll
21. Add Blinking Text
22. Make multiple alerts cycle
23. need to add "force" on an option for a module like "alert" so it always show up on top
24. For "positions" allow aliases: "fps_strip": "bottom_left" so that moddefs are not tied to screen positions
25. Different display configurations need to be detected and handled (same as device drivers, above?)
26. Generic Text Item (scrolling horizontally and vertically, blinking color)
27. Add strong typing and checks on config data
28. Better logging (_debug, _info, _warn, _error) at the module level
29. Add sound - weather alerts for example
6. WebServer seems to lag - lacking CPU time?
30. Better solution for web-based logging (dribbling stderr/stdout to text file is not a good solution)
31. Make the Control Panel web page display current status in the toggles (currently always shows "off")

## DONE

1. update gfx object so "set_font(font_name, font_size)" is 'permanent'
    - currently it only sets the gfx.font, but not gfx.font_name, gfx.font_size
    - likewise remove reset_font()
    - originally the idea was set_font() would temporarily set the font and reset_font() would restore it
    - but with gfx = copy.copy(self.gfx) we can manipulate the gfx obj and font and not worry about resetting

3. exec() should return True if a render() is needed and False otherwise

4. render() should be called only if exec() returns True

5. render()
    - render(force=True) implies a full re-rendering (clear the old, redraw the new)
    - render(force=False) implies a minimal repaint of only what has updated since the last render
    - it is up to the module to determine what needs updating

8. Convert all forms of color to 32-bit integer for use in PIL "I" mode

9. Handle Portrait mode

11. text_box() needs text_wrap abilities
    - None (just a straight line of text)
    - Wrap (split on character boundaries)
    - Word Wrap (split on word boundaries)
    - Handle (or ignore) newlines
    - Boundary clipping

13. Update screen.draw() methods to accept tuples rather than parms

14. Move configurations to separate files

15. Add webserver to control modules via events

14. Add generalized class for "window" that has header/body/footer (PMCard)

16. shore-up event processing with "onEventName()" events (can be overridden by overriding onEvent())

17.  display write-to-file and webserver

2. refresh the entire display based upon some event
    - this means clearing the display and forcing all objects to re-render

7. Some sort of full refresh. PyMirror would clear the screen and all render methods would be called with "force=True"

1. add try/catch surrounding PyMirror main loop to catch errors in module processing

20. add text animations, like fade in / fade out - commented out

12. Boundary clipping

2. webserver
    1. debug on / off
    2. send alert
    3. turn on / off preview
10. optimize API calls (cache to disk) for weather, news
1. fix week number (use iso date)
7. Check on news module - "None" and missing data sometimes
7. update debug mode to include times for rendering modules
8. temporary: send output from ./run.sh to a log file 
- potentially make accessible from web front end
