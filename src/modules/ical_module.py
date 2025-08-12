# ical_module.py
# https://openicalmap.org/api/one-call-3#current

from dataclasses import dataclass
import sys
import requests
from datetime import date, datetime, timedelta, timezone
from ics import Calendar

import events
from pymirror.pmcard import PMCard
from pymirror.pmwebapi import PMWebApi

@dataclass
class ICalConfig:
    url: str = None
    cache_file: str = "./caches/ical.json"
    refresh_minutes: int = 60
    max_events: int = 10
    time_format: str = "%-I:%M %p"

class IcalModule(PMCard):
    def __init__(self, pm, config):
        super().__init__(pm, config)
        self._ical = ICalConfig(**config.ical.__dict__)
        self.timer.set_timeout(1)  # refresh right away
        self.ical_response = None
        self.api = PMWebApi(self._ical.url, self._ical.cache_file, self._ical.refresh_minutes * 60)


    def exec(self) -> bool:
        is_dirty = super().exec()
        if not self.timer.is_timedout(): return is_dirty # early exit if not timed out

        self.timer.set_timeout(self._ical.refresh_minutes * 60 * 1000)
        self.ical_response = self.api.get_text()
        events = Calendar(self.ical_response).timeline.included(datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(days=365))
        event_str = "\n"
        event_cnt = 0
        now = datetime.now(timezone.utc) + timedelta(hours=24) 
        for event in events:
            event_cnt += 1
            if event_cnt > self._ical.max_events:
                break
            if event.begin.datetime > now:
                break
            if event.all_day:
                event_str += f"{event.name}\n"
            else:
                event_str += f"{event.begin.strftime(self._ical.time_format)}: {event.name}\n"

        self.update(
            "iCalendar\n" + now.astimezone().strftime("%A, %b %-d"),
            event_str,
            "last updated\n" + now.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return True # state changed
