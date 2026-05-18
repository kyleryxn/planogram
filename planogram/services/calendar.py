from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from planogram.models import ScheduleEvent

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class NeedsAuthError(Exception):
    pass


def get_credentials(oauth_credentials_path: Path, token_path: Path) -> Credentials:
    creds: Optional[Credentials] = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds, token_path)
        return creds

    raise NeedsAuthError("Google Calendar authorization required.")


def initiate_auth_flow(
    oauth_credentials_path: Path, redirect_uri: str
) -> tuple[str, Flow]:
    flow = Flow.from_client_secrets_file(
        str(oauth_credentials_path),
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url, flow


def handle_auth_callback(
    flow: Flow, authorization_response: str, token_path: Path
) -> Credentials:
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    _save_token(creds, token_path)
    return creds


def _save_token(creds: Credentials, token_path: Path) -> None:
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())


def push_events(
    events: list[ScheduleEvent],
    credentials: Credentials,
    calendar_id: str,
    timezone: str,
    notification_minutes: int | None = None,
) -> list[str]:
    service = build("calendar", "v3", credentials=credentials)
    links = []
    for event in events:
        body = _build_event_body(event, timezone, notification_minutes)
        result = service.events().insert(calendarId=calendar_id, body=body).execute()
        links.append(result.get("htmlLink", ""))
    return links


def _build_event_body(event: ScheduleEvent, timezone: str, notification_minutes: int | None = None) -> dict:
    base = {
        "summary": event.title,
        "description": event.description or "",
        "location": event.location or "",
    }
    if event.color_id:
        base["colorId"] = event.color_id
    if notification_minutes is None:
        base["reminders"] = {"useDefault": True}
    elif notification_minutes == 0:
        base["reminders"] = {"useDefault": False, "overrides": []}
    else:
        base["reminders"] = {
            "useDefault": False,
            "overrides": [{"method": "popup", "minutes": notification_minutes}],
        }
    if event.end_time:
        base["start"] = {
            "dateTime": datetime.combine(event.date, event.start_time).isoformat(),
            "timeZone": timezone,
        }
        base["end"] = {
            "dateTime": datetime.combine(event.date, event.end_time).isoformat(),
            "timeZone": timezone,
        }
    else:
        base["start"] = {"date": event.date.isoformat()}
        base["end"] = {"date": event.date.isoformat()}
    return base
