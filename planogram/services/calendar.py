"""Google Calendar OAuth 2.0 flow and event creation helpers.

Credentials are persisted to disk after the first successful authorization, so
later runs skip the consent screen entirely. The OAuth flow uses
``prompt="consent"`` to always request a refresh token, which is required for
long-lived offline access.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from planogram.models import ScheduleEvent

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class NeedsAuthError(Exception):
    """Raised when no valid Google OAuth token exists and user authorization is required."""


def get_credentials(oauth_credentials_path: Path, token_path: Path) -> Credentials:
    """Load and return valid Google OAuth credentials from the disk.

    Attempts to load a previously saved token, refreshing it automatically if it
    expired.  Raises ``NeedsAuthError`` if no usable token exists, signaling
    the caller to redirect the user through the OAuth consent flow.

    Args:
        oauth_credentials_path: Path to the OAuth client secrets JSON file.
        token_path: Path where the user token JSON is stored after authorization.

    Returns:
        Valid ``Credentials`` ready for use with Google API clients.

    Raises:
        NeedsAuthError: If no token file exists or the token cannot be refreshed.
    """
    creds: Optional[Credentials] = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.valid:
        logger.info("Credentials loaded from %s", token_path)
        return creds

    if creds and creds.expired and creds.refresh_token:
        logger.info("Refreshing expired credentials")
        creds.refresh(Request())
        _save_token(creds, token_path)
        return creds

    logger.warning("No valid credentials found — authorization required")
    raise NeedsAuthError("Google Calendar authorization required.")


def initiate_auth_flow(
    oauth_credentials_path: Path, redirect_uri: str
) -> tuple[str, Flow]:
    """Create a Google OAuth 2.0 authorization flow and return the consent URL.

    ``prompt="consent"`` is passed to ensure Google always returns a refresh
    token, even if the user has previously authorized the application.

    Args:
        oauth_credentials_path: Path to the OAuth client secrets JSON file.
        redirect_uri: The URI Google will redirect to after the user consents.  Must
            match a URI registered in the Google Cloud Console.

    Returns:
        A tuple of ``(auth_url, flow)`` where ``auth_url`` is the Google consent
        page URL to redirect the user to and ``flow`` is the in-progress
        ``Flow`` object that must be stored until the callback arrives.
    """
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
    """Exchange the OAuth authorization code for credentials and persist them.

    Args:
        flow: The ``Flow`` object created by ``initiate_auth_flow``, retrieved
            from the in-memory pending flows store.
        authorization_response: The full callback URL including the ``code``
            query parameter returned by Google.
        token_path: Path where the resulting token JSON will be written.

    Returns:
        Valid ``Credentials`` containing access and refresh tokens.
    """
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    _save_token(creds, token_path)
    return creds


def _save_token(creds: Credentials, token_path: Path) -> None:
    """Persist OAuth credentials to disk as JSON.

    Creates parent directories if they do not exist.

    Args:
        creds: The credentials to serialize.
        token_path: Destination file path.
    """
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())


def push_events(
    events: list[ScheduleEvent],
    credentials: Credentials,
    calendar_id: str,
    timezone: str,
    notification_minutes: int | None = None,
) -> list[str]:
    """Insert a list of events into Google Calendar and return their HTML links.

    Args:
        events: Events to create, in the order they will be inserted.
        credentials: Valid Google OAuth credentials scoped to calendar events.
        calendar_id: Target calendar identifier (``"primary"`` for the default).
        timezone: IANA timezone name applied to all timed events
            (e.g. ``"America/New_York"``).
        notification_minutes: Override for the popup reminder time in minutes.
            Pass ``None`` to use the calendar default, ``0`` to suppress all
            reminders, or a positive integer for a custom lead time.

    Returns:
        List of ``htmlLink`` URLs for the created events, in the same order as
        the input list.
    """
    logger.info("Pushing %d event(s) to calendar %r", len(events), calendar_id)
    t0 = time.perf_counter()
    service = build("calendar", "v3", credentials=credentials)
    links = []
    for event in events:
        body = build_event_body(event, timezone, notification_minutes)
        result = service.events().insert(calendarId=calendar_id, body=body).execute()
        link = result.get("htmlLink", "")
        logger.info("Created event %r on %s", event.title, event.date)
        links.append(link)
    logger.info("Pushed %d event(s) in %.1fs", len(links), time.perf_counter() - t0)
    return links


def build_event_body(
    event: ScheduleEvent,
    timezone: str,
    notification_minutes: int | None = None,
) -> dict:
    """Construct the Google Calendar API event resource dictionary.

    Creates a timed event when ``end_time`` is set, or an all-day event when it
    is absent.  Reminder overrides are applied according to
    ``notification_minutes``.

    Args:
        event: The schedule event to convert.
        timezone: IANA timezone name for ``start`` and ``end`` dateTime fields.
        notification_minutes: See ``push_events`` for semantics.

    Returns:
        A dictionary conforming to the Google Calendar Events resource schema,
        ready to pass to ``events().insert()``.
    """
    base: dict = {
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
