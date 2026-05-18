"""Service layer for Planogram.

Modules:
    parser: Two-pass Claude AI pipeline — visual transcription then structured
              JSON extraction — that converts a schedule image into ScheduleEvent
              objects.
    calendar: Google Calendar OAuth flow and event push helpers.
"""
