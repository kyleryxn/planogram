from pathlib import Path

REDIRECT_URI = "https://localhost:8000/auth/callback"

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.events.readonly",
]

CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"
