"""Google OAuth 2.0 authorization routes.

Exposes two endpoints that together implement the server-side OAuth flow:

- ``GET /auth/start`` generates the Google consent URL and stores the in-progress
  ``Flow`` object in an in-memory dict keyed by session ID, then redirects the
  browser to Google.
- ``GET /auth/callback`` receives the authorization code from Google, exchanges
  it for credentials, persists them to disk, and either pushes any events that
  were pending before the redirect or returns the user to the review page.

The in-memory flow store (``_pending_flows``) is acceptable for a single-user
personal tool running as a single process.  It would need a shared cache (e.g.
Redis) for multi-process or multi-user deployments.
"""

import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError

from planogram.config import get_settings
from planogram.models import ParsedSchedule, ScheduleEvent
from planogram.services import calendar as cal_service

router = APIRouter()
templates = Jinja2Templates(directory="planogram/templates")
TMP_DIR = Path("tmp")

# In-memory flow store — acceptable for single-user personal tool
_pending_flows: dict[str, Flow] = {}


@router.get("/auth/start")
async def auth_start(request: Request, session_id: str):
    """Initiate the Google OAuth 2.0 consent flow.

    Creates an authorization ``Flow``, stores it under ``session_id``, and
    redirects the browser to the Google consent screen.  The ``session_id`` is
    used later in the callback to match the flow and locate any pending events.

    Args:
        request: The incoming FastAPI request object.
        session_id: The UUID of the session whose events are awaiting push.
            Stored as the key in ``_pending_flows`` so the callback can
            retrieve the correct ``Flow`` instance.

    Returns:
        A redirect response to the Google OAuth consent URL.
    """
    settings = get_settings()
    auth_url, flow = cal_service.initiate_auth_flow(
        settings.google_oauth_credentials_path,
        settings.google_oauth_redirect_uri,
    )
    _pending_flows[session_id] = flow
    return RedirectResponse(url=auth_url)


@router.get("/auth/callback", name="auth_callback")
async def auth_callback(request: Request):
    """Handle the Google OAuth 2.0 callback and push any pending events.

    Retrieves the stored ``Flow`` for the oldest pending session, exchanges the
    authorization code for credentials, and persists them to disk.  If events
    were serialized to a ``_pending.json`` file before the OAuth redirect they
    are pushed to Google Calendar immediately; otherwise the user is sent back
    to the review page to confirm manually.

    Args:
        request: The incoming FastAPI request object.  The full URL (including
            the ``code`` query parameter appended by Google) is passed to
            ``handle_auth_callback`` for token exchange.

    Returns:
        An HTML response rendering ``success.html`` if pending events were
        pushed successfully, a redirect to ``/review`` if no pending events
        existed, or a re-rendered review page on Google Calendar API error.
    """
    settings = get_settings()

    session_id = next(iter(_pending_flows), None)
    if session_id is None:
        return RedirectResponse(url="/?error=auth_failed")

    flow = _pending_flows.pop(session_id)
    creds = cal_service.handle_auth_callback(
        flow,
        authorization_response=str(request.url),
        token_path=settings.google_token_path,
    )

    # Push any events that were pending before the OAuth redirect
    pending_path = TMP_DIR / f"{session_id}_pending.json"
    if pending_path.exists():
        event_jsons = json.loads(pending_path.read_text())
        events = [ScheduleEvent.model_validate_json(ej) for ej in event_jsons]

        try:
            links = cal_service.push_events(
                events, creds, settings.google_calendar_id, settings.timezone
            )
        except HttpError as exc:
            schedule = ParsedSchedule(events=events, raw_ocr_text="", source_image_name="")
            return templates.TemplateResponse(
                request, "review.html",
                context={"schedule": schedule, "session_id": session_id, "error": f"Google Calendar error: {exc}"},
                status_code=502,
            )
        finally:
            pending_path.unlink(missing_ok=True)
            (TMP_DIR / f"{session_id}.json").unlink(missing_ok=True)

        return templates.TemplateResponse(
            request, "success.html",
            context={"links": links, "count": len(events)},
        )

    return RedirectResponse(url=f"/review?id={session_id}", status_code=303)
