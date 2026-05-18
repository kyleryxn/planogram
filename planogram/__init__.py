"""Planogram — schedule image to Google Calendar.

Uploads a photo of a printed or handwritten work schedule, extracts events
using Claude AI, and pushes confirmed events to Google Calendar.

Packages:
    services: OCR, AI parsing, and Google Calendar integration.
    routes:   FastAPI route handlers for upload, review, and OAuth flows.
"""
