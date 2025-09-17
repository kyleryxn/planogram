# planogram/routes/calendar.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import anyio
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from google.auth.transport.requests import Request as GRequest
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession

from planogram.database import get_async_session
from planogram.google_oauth.token_repo import get_user_creds_db, save_user_creds_db
from planogram.routes.asset_registry import get_static, get_template
from planogram.routes.home import templates

router = APIRouter(prefix="/calendar", tags=["calendar"])
DEMO_USER_KEY = "demo-user"


async def _get_service(db: AsyncSession):
    """Return an authenticated Google Calendar service, refreshing tokens if needed."""
    creds = await get_user_creds_db(db, DEMO_USER_KEY)
    if not creds:
        raise HTTPException(status_code=401, detail="Not authorized with Google")

    if not creds.valid:
        if getattr(creds, "refresh_token", None):
            # Refresh is sync; run in a worker thread to avoid blocking the event loop
            await anyio.to_thread.run_sync(lambda: creds.refresh(GRequest()))
            await save_user_creds_db(db, DEMO_USER_KEY, creds)
        else:
            raise HTTPException(
                status_code=401,
                detail="Token expired and no refresh token. Re-consent with access_type=offline & prompt=consent.",
            )

    # googleapiclient is sync; build it in a worker thread too
    service = await anyio.to_thread.run_sync(
        lambda: build("calendar", "v3", credentials=creds, cache_discovery=False)
    )
    return service

@router.get("/calendars", response_class=HTMLResponse)
async def calendars_page(request: Request, db: AsyncSession = Depends(get_async_session)):
    """Render a list of the user's calendars."""
    service = await _get_service(db)
    resp = await anyio.to_thread.run_sync(lambda: service.calendarList().list().execute())
    items = resp.get("items", [])

    main_css_url = request.url_for("static", path=get_static("main_css"))

    return templates.TemplateResponse(
        get_template("calendars"),
        {
            "request": request,
            "title": "Planogram",
            "main_css_url": main_css_url,
            "calendars": items
        },
    )

@router.get("/events", response_class=HTMLResponse)
async def events_page(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    calendar_id: str = Query("primary"),
    max_results: int = Query(10, ge=1, le=2500),
    time_min: Optional[datetime] = Query(None, description="RFC3339; defaults to now"),
    time_max: Optional[datetime] = None,
    page_token: Optional[str] = None,
):
    """Render upcoming events for a calendar (default: primary)."""
    service = await _get_service(db)

    if time_min is None:
        time_min = datetime.now(timezone.utc)

    params = dict(
        calendarId=calendar_id,
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results,
        timeMin=time_min.astimezone(timezone.utc).isoformat(),
    )

    if time_max:
        params["timeMax"] = time_max.astimezone(timezone.utc).isoformat()

    if page_token:
        params["pageToken"] = page_token

    resp = await anyio.to_thread.run_sync(lambda: service.events().list(**params).execute())

    # Prepare a lightweight list for the template (handles all-day events too)
    def _when(ev, key):
        v = (ev.get(key) or {})
        return v.get("dateTime") or v.get("date") or ""

    events = [
        {
            "id": ev.get("id", ""),
            "summary": ev.get("summary", "(no title)"),
            "start": _when(ev, "start"),
            "end": _when(ev, "end"),
            "location": ev.get("location", ""),
            "hangoutLink": ev.get("hangoutLink", ""),
            "htmlLink": ev.get("htmlLink", ""),
        }
        for ev in resp.get("items", [])
    ]

    main_css_url = request.url_for("static", path=get_static("main_css"))

    return templates.TemplateResponse(
        get_template("events"),
        {
            "request": request,
            "title": "Planogram",
            "main_css_url": main_css_url,
            "events": events
        },
    )
