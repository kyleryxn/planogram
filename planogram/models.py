"""Pydantic data models shared across the application."""

from __future__ import annotations

from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field


class ScheduleEvent(BaseModel):
    """A single calendar event extracted from a schedule image.

    Attributes:
        title: Event summary shown in Google Calendar.
        date: Calendar date of the event in YYYY-MM-DD format.
        start_time: Event start time in 24-hour HH:MM format.
        end_time: Optional end time.  When absent, the event is created as an
            all-day event in Google Calendar.
        description: Optional free-text body copied to the calendar event
            description field.
        location: Optional place name or address shown in Google Calendar.
        color_id: Optional Google Calendar color identifier (``"1"``–``"11"``).
            When absent, the calendar's default event color is used.
    """

    title: str
    date: date
    start_time: time
    end_time: Optional[time] = None
    description: Optional[str] = None
    location: Optional[str] = None
    color_id: Optional[str] = None


class ParsedSchedule(BaseModel):
    """The full result of processing a single uploaded schedule image.

    Attributes:
        events: Ordered list of events extracted from the image.
        raw_ocr_text: The intermediate transcription produced by the first
            Claude pass, preserved for display on the review page.
        source_image_name: Original filename of the uploaded file, shown on
            the review page for reference.
    """

    events: list[ScheduleEvent] = Field(default_factory=list)
    raw_ocr_text: str
    source_image_name: str
