import datetime
from pymirror.utils import to_int
from pymirror.pmlogger import _debug

class Crontab:
    def __init__(self, crontab: list[str]):
        self.crontab = crontab or []
        self.last_crontime = None
        self.crontime = self._update_crontime()
        self.cron_now = None

    def check(self) -> list[int]:
        """ returns a list of indices of crontabs that match the current time"""
        results = []
        self._update_crontime()
        if self.crontime == self.last_crontime:
            return results
        self.last_crontime = self.crontime
        self.cron_now = self._to_cron_int(self.crontime)
        for i in range(len(self.crontab)):
            if self._compare_cronstring(self.crontab[i]):
                results.append(i)
        return results

    def _update_crontime(self):
        # Get current time with second resolution only
        self.crontime = datetime.datetime.now().replace(microsecond=0)
        return self.crontime

    def _to_cron_int(self, now) -> list:
        weekday = (now.weekday() + 1) % 7
        result = [now.second, now.minute, now.hour, now.day, now.month, weekday]
        return result

    def _compare_cronstring(self, cronstring: str) -> bool:
        cron_parts = cronstring.split(" ")
        _debug(cron_parts, self.cron_now)
        ## pad with wildcards
        ## we might want to preprocess this at __init__ for performance
        while len(cron_parts) < 6:
            cron_parts = ["*"] + cron_parts
        for i in range(len(cron_parts)):
            for pattern in cron_parts[i].split(","):
                if pattern == "*":
                    ## wild card matches anything
                    _debug(f"{pattern}={self.cron_now[i]} Wildcard match found")
                    break
                pattern = to_int(pattern, -1)
                if pattern == self.cron_now[i]:
                    _debug(f"{pattern}={self.cron_now[i]} matches")
                    break
            else:
                _debug(f"{i}: Cron part {cron_parts[i]} did not match {self.cron_now[i]}")
                return False
        _debug(f"{i}: All cron parts matched successfully")
        return True