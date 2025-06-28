# TODO List

2. refresh the entire display based upon some event
    - this means clearing the display and forcing all objects to re-render

6. Hot Reload of config.json
    - if config.json is updated then dispose of old modules and reload

7. Some sort of full refresh. PyMirror would clear the screen and all render methods would be called with "force=True"

10. handle exceptions

12. Boundary clipping ?

13. weather.py - error checking for bad api results

14. Add generalized class for "window" that has header/body/footer

16. shore-up event processing with "onEventName()" events

17. add device drivers for display to include write-to-file and webserver

18. add try/catch surrounding PyMirror main loop to catch errors in module processing

19. Better error handling

# DONE

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
