# ical_module.py
# https://openicalmap.org/api/one-call-3#current

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from ics import Calendar

from pymirror.pmcard import PMCard
from pymirror.pmwebapi import PMWebApi
from pymirror.utils import strftime_by_example
from pymirror.pmlogger import _debug, _error

@dataclass
class ICalConfig:
    url: str = None
    cache_file: str = "./caches/ical.json"
    refresh_minutes: int = 60
    max_events: int = 10
    number_days: int = 7
    time_format: str = strftime_by_example("0:00 PM")
    show_all_day_events: bool = True
    all_day_format: str = strftime_by_example("Jan-1")

class IcalModule(PMCard):
    def __init__(self, pm, config):
        super().__init__(pm, config)
        self._ical = ICalConfig(**config.ical.__dict__)
        self.timer.set_timeout(1)  # refresh right away
        self.ical_response = None
        self.api = PMWebApi(self._ical.url, self._ical.cache_file, self._ical.refresh_minutes * 60)
        self.all_day_format = strftime_by_example(self._ical.all_day_format)
        self.time_format = strftime_by_example(self._ical.time_format)

    def _dump_event(self, event):
        _debug(event.name)
        _debug("...begin:", event.begin)
        _debug("...end:", event.end)
        _debug("...duration:", event.duration)
        _debug("...uid:", event.uid)
        _debug("...description:", event.description)
        _debug("...created:", event.created)
        _debug("...last_modified:", event.last_modified)
        _debug("...location:", event.location)
        _debug("...url:", event.url)
        _debug("...transparent:", event.transparent)
        _debug("...alarms:", event.alarms)
        _debug("...attendees:", event.attendees)
        _debug("...categories:", event.categories)
        _debug("...status:", event.status)
        _debug("...organizer:", event.organizer)
        _debug("...geo:", event.geo)
        _debug("...classification:", event.classification)
        _debug("...extra:", event.extra)

    def exec(self) -> bool:
        is_dirty = super().exec()
        if not self.timer.is_timedout(): return is_dirty # early exit if not timed out

        # self.timer.set_timeout(self._ical.refresh_minutes * 60 * 1000)
        self.ical_response = self.api.get_text()
        epoch = datetime(1980, 1, 1, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        later = now + timedelta(hours=24 * self._ical.number_days)
        cal = Calendar(self.ical_response)
        events = cal.timeline.included(epoch, later)

        event_str = ""
        all_day_str = ""
        event_cnt = 0
        for event in events:
            if event.name == "AASHR Weekly Mtg":
                self._dump_event(event)
            if event_cnt > self._ical.max_events:
                break
            if event.begin.datetime < now:
                continue
            event_cnt += 1
            if event.all_day and self._ical.show_all_day_events:
                all_day_str += f"{event.begin.strftime(self.all_day_format)}: {event.name}\n"
            else:
                event_str += f"{event.begin.strftime(self.time_format)}: {event.name}\n"
        event_str += "\n" + all_day_str
        if self._ical.number_days > 1:
            format = strftime_by_example("Monday, Jan 1")
            header_str = f"iCalendar\n{now.strftime(format)} - {later.strftime(format)}"
        self.update(
            header_str,
            event_str or "No Events to Show",
            "last updated\n" + now.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return True # state changed
