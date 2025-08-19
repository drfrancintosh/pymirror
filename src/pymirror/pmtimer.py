import time

class PMTimer:
    def __init__(self, ms=0):
        self.timeout = 0
        self.set_timeout(ms)
        
    def set_timeout(self, ms):
        if not ms or ms < 0: self.timeout = 0 ## disable timer
        else: self.timeout = time.time() + ms / 1000

    def is_timedout(self, reset_ms: int = None):
        if not self.timeout: return False # disabled timer always returns False
        if time.time() < self.timeout:
            return False ## we're not timed out yet
        else:
            if reset_ms != None:
                self.set_timeout(reset_ms) ## reset timer (0=disable, 1=1ms retry, None = perpetuate)
            return True
