from __future__ import annotations
from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field


class ScheduleEvent(BaseModel):
    title: str
    date: date
    start_time: time
    end_time: Optional[time] = None
    description: Optional[str] = None
    location: Optional[str] = None


class ParsedSchedule(BaseModel):
    events: list[ScheduleEvent] = Field(default_factory=list)
    raw_ocr_text: str
    source_image_name: str
