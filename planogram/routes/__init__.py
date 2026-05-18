"""FastAPI route handlers for Planogram.

Modules:
    upload: GET / serves the upload form; POST /upload processes the image and
            redirects to the review page.
    review: GET /review renders the editable event table; POST /confirm pushes
            confirmed events to Google Calendar.
    auth:   GET /auth/start and GET /auth/callback handle the Google OAuth 2.0
            flow.
"""
