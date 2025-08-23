# ical_module.py
# https://openicalmap.org/api/one-call-3#current

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import time
from ics import Calendar

from pymirror.pmcard import PMCard
from pymirror.pmwebapi import PMWebApi
from pymirror.utils import SafeNamespace, strftime_by_example
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
        self.timer.set_timeout(self._ical.refresh_minutes * 60 * 1000)
        self.ical_response = None
        self.api = PMWebApi(self._ical.url, self._ical.refresh_minutes * 60, self._ical.cache_file)
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

    def _parse_rrule(self, rrule: str, now: datetime) -> dict:
        """Parse the RRULE string into a dictionary."""
        ## NOTE: Original (raw) values are in UPPERCASE
        ## NOTE: The parsed values are in lowercase
        dow = {
            "SU": 6,
            "MO": 0,
            "TU": 1,
            "WE": 2,
            "TH": 3,
            "FR": 4,
            "SA": 5
        }
        rules = {}
        for part in rrule.split(";"):
            key, value = part.split("=", 1)
            key = key.strip().upper()
            value = value.strip().upper()
            rules[key] = value
            if key == "UNTIL":
                if len(value) == 16:  # YYYYMMDDTHHMMSSZ
                    rules[key.lower()] = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
                elif len(value) == 8:  # YYYYMMDD
                    rules[key.lower()] = datetime.strptime(value, "%Y%m%d").replace(tzinfo=timezone.utc)
            elif key in ["BYSECOND", "BYMINUTE", "BYHOUR", "BYMONTHDAY", "BYYEARDAY", "BYWEEKNO", "BYMONTH", "BYSETPOS"]:
                rules[key.lower()] = [int(s) for s in value.split(",")]
            elif key in ["BYDAY"]:
                rules[key.lower()] = [dow.get(s, s) for s in value.split(",")]
            elif key in ["WKST"]:
                rules[key.lower()] = dow.get(value, value)
            else:
                if value.isdigit():
                    rules[key.lower()] = int(value)
        if not rules.get("UNTIL"):
            ## default to now
            rules["UNTIL"] = now.strftime("%Y%m%dT%H%M%SZ")
            rules["until"] = now
        return SafeNamespace(**rules)

    def _get_rrule(self, event, now: datetime) -> bool:
        for _line in event.extra:
            line = str(_line).strip()
            if "RRULE:" == line[0:6]:
                return self._parse_rrule(line[6:], now)
        return None

    def _generate_recurring_dates(self, event, now: datetime) -> list:
        rrule = self._get_rrule(event, now)
        if not rrule:
            return []

        # Parse the RRULE and generate the recurring dates
        # This is a simplified example and may need to be adjusted for real RRULE parsing
        dates = []
        for line in rrule.splitlines():
            if line.startswith("FREQ=WEEKLY"):
                # Generate weekly dates
                for i in range(1, 5):  # Next 4 weeks
                    dates.append(event.begin + timedelta(weeks=i))
        return dates

    def exec(self) -> bool:
        is_dirty = super().exec()
        if not self.timer.is_timedout(): return is_dirty # early exit if not timed out
        self.timer.reset()

        self.ical_response = self.api.fetch_text(blocking=False)
        if not self.ical_response:
            # non-blocking call or error?
            if self.api.error:
                _error(f"Failed to fetch iCalendar data from {self.api.url}: {self.api.error}")
            self.update(
                "iCalendar",
                "(loading...)",
                datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            )
            self.timer.reset(1000)
            return False
        print("got data...")
        epoch = datetime(1980, 1, 1, tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        later = now + timedelta(hours=24 * self._ical.number_days)
        cal = Calendar(self.ical_response)
        events = cal.timeline.included(epoch, later)

        event_str = ""
        all_day_str = ""
        event_cnt = 0
        daily_events = []
        all_day_events = []
        for event in events:
            rrule = self._get_rrule(event, now)
            if rrule and rrule.until >= now:
                # print(f"Event: {event.name}({event.all_day}) - {event.begin} to {event.end}")
                # print(f"RRULE: {rrule}\n")
                # new_events = self._generate_recurring_dates(event, now, later)
                pass
            if event_cnt > self._ical.max_events:
                break
            if event.begin.datetime < now:
                continue
            if event.all_day and self._ical.show_all_day_events:
                all_day_events.append(event)
            else:
                daily_events.append(event)

        for event in daily_events:
            event_str += f"{event.begin.strftime(self.time_format)}: {event.name}\n"
        for event in all_day_events:
            all_day_str += f"{event.begin.strftime(self.all_day_format)}: {event.name}\n"
        if self._ical.number_days > 1:
            format = strftime_by_example("Monday, Jan 1")
            header_str = f"iCalendar\n{now.strftime(format)} - {later.strftime(format)}"
        self.update(
            header_str,
            event_str or "No Events to Show",
            "last updated\n" + now.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        )
        print("updated...")
        return True # state changed
