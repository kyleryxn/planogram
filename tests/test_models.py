"""Tests for Pydantic data models."""

from datetime import date, time

import pytest
from pydantic import ValidationError

from planogram.models import ParsedSchedule, ScheduleEvent


class TestScheduleEvent:
    def test_valid_minimal(self):
        event = ScheduleEvent(title="Work", date=date(2025, 1, 6), start_time=time(9, 0))
        assert event.title == "Work"
        assert event.end_time is None
        assert event.description is None
        assert event.location is None
        assert event.color_id is None

    def test_valid_full(self):
        event = ScheduleEvent(
            title="Work",
            date=date(2025, 1, 6),
            start_time=time(9, 0),
            end_time=time(17, 0),
            description="Evening shift",
            location="123 Main St",
            color_id="7",
        )
        assert event.end_time == time(17, 0)
        assert event.location == "123 Main St"
        assert event.color_id == "7"

    def test_missing_title_raises(self):
        with pytest.raises(ValidationError):
            ScheduleEvent(date=date(2025, 1, 6), start_time=time(9, 0))

    def test_missing_date_raises(self):
        with pytest.raises(ValidationError):
            ScheduleEvent(title="Work", start_time=time(9, 0))

    def test_missing_start_time_raises(self):
        with pytest.raises(ValidationError):
            ScheduleEvent(title="Work", date=date(2025, 1, 6))

    def test_invalid_date_raises(self):
        with pytest.raises(ValidationError):
            ScheduleEvent(title="Work", date="not-a-date", start_time=time(9, 0))

    def test_invalid_time_raises(self):
        with pytest.raises(ValidationError):
            ScheduleEvent(title="Work", date=date(2025, 1, 6), start_time="25:99")


class TestParsedSchedule:
    def test_empty_events_by_default(self):
        schedule = ParsedSchedule(raw_ocr_text="raw", source_image_name="file.jpg")
        assert schedule.events == []

    def test_with_events(self):
        event = ScheduleEvent(title="Work", date=date(2025, 1, 6), start_time=time(9, 0))
        schedule = ParsedSchedule(
            events=[event],
            raw_ocr_text="raw",
            source_image_name="schedule.png",
        )
        assert len(schedule.events) == 1
        assert schedule.events[0].title == "Work"

    def test_missing_raw_ocr_text_raises(self):
        with pytest.raises(ValidationError):
            ParsedSchedule(source_image_name="file.jpg")

    def test_missing_source_image_name_raises(self):
        with pytest.raises(ValidationError):
            ParsedSchedule(raw_ocr_text="raw")
