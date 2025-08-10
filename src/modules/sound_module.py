import pygame
from pymirror.pmmodule import PMModule
from pymirror.pmlogger import _error, _debug

class SoundModule(PMModule):
    def __init__(self, pm, config):
        super().__init__(pm, config)
        self._sound = config.sound
        self.subscribe(["SoundEvent"])
        # Initialize the mixer
        pygame.mixer.init()

    def render(self, force: bool = False) -> bool:
        pass

    def onSoundEvent(self, event):
        _debug(f"SoundModule: Playing sound {event.filename}")
        try:
            pygame.mixer.music.load(event.filename)
            pygame.mixer.music.play()
        except Exception as e:
            _error(f"Error playing sound {event.filename}: {e}")

    def exec(self) -> bool:
        # This module does not need to execute anything periodically
        return False
