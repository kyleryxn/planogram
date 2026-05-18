"""Tests for the calendar service helper functions."""

from datetime import date, time

from planogram.models import ScheduleEvent
from planogram.services.calendar import build_event_body


def make_event(**kwargs) -> ScheduleEvent:
    """Return a ScheduleEvent with sensible defaults for testing."""
    defaults = {
        "title": "Work",
        "date": date(2025, 1, 6),
        "start_time": time(9, 0),
    }
    defaults.update(kwargs)
    return ScheduleEvent(**defaults)


TZ = "America/New_York"


class TestBuildEventBody:
    def test_timed_event_datetimes(self):
        event = make_event(end_time=time(17, 0))
        body = build_event_body(event, TZ)
        assert body["start"]["dateTime"] == "2025-01-06T09:00:00"
        assert body["end"]["dateTime"] == "2025-01-06T17:00:00"
        assert body["start"]["timeZone"] == TZ
        assert body["end"]["timeZone"] == TZ

    def test_all_day_event_no_end_time(self):
        event = make_event()
        body = build_event_body(event, TZ)
        assert body["start"] == {"date": "2025-01-06"}
        assert body["end"] == {"date": "2025-01-06"}
        assert "timeZone" not in body["start"]

    def test_default_reminder_uses_calendar(self):
        body = build_event_body(make_event(), TZ, notification_minutes=None)
        assert body["reminders"] == {"useDefault": True}

    def test_zero_minutes_suppresses_reminders(self):
        body = build_event_body(make_event(), TZ, notification_minutes=0)
        assert body["reminders"] == {"useDefault": False, "overrides": []}

    def test_custom_reminder_minutes(self):
        body = build_event_body(make_event(), TZ, notification_minutes=30)
        assert body["reminders"]["useDefault"] is False
        assert body["reminders"]["overrides"] == [{"method": "popup", "minutes": 30}]

    def test_color_id_included(self):
        body = build_event_body(make_event(color_id="7"), TZ)
        assert body["colorId"] == "7"

    def test_no_color_id_omitted(self):
        body = build_event_body(make_event(), TZ)
        assert "colorId" not in body

    def test_location_included(self):
        body = build_event_body(make_event(location="123 Main St"), TZ)
        assert body["location"] == "123 Main St"

    def test_empty_location_is_empty_string(self):
        body = build_event_body(make_event(location=None), TZ)
        assert body["location"] == ""

    def test_summary_matches_title(self):
        body = build_event_body(make_event(title="Night Shift"), TZ)
        assert body["summary"] == "Night Shift"
