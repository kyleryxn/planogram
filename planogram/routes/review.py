import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from googleapiclient.errors import HttpError

from planogram.config import get_settings
from planogram.models import ParsedSchedule, ScheduleEvent
from planogram.services import calendar as cal_service

router = APIRouter()
templates = Jinja2Templates(directory="planogram/templates")
TMP_DIR = Path("tmp")


@router.get("/review")
async def review(request: Request, id: str):
    tmp_path = TMP_DIR / f"{id}.json"
    if not tmp_path.exists():
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    schedule = ParsedSchedule.model_validate_json(tmp_path.read_text())
    settings = get_settings()
    return templates.TemplateResponse(
        request, "review.html",
        context={
            "schedule": schedule,
            "session_id": id,
            "maps_api_key": settings.google_maps_api_key,
        },
    )


@router.post("/confirm")
async def confirm(request: Request):
    settings = get_settings()
    form = await request.form()
    session_id = str(form.get("session_id", ""))

    notif_raw = str(form.get("notification_minutes", ""))
    if notif_raw == "":
        notification_minutes = None
    else:
        notification_minutes = int(notif_raw)

    events: list[ScheduleEvent] = []
    index = 0
    while f"title_{index}" in form:
        location_raw = str(form.get(f"location_{index}") or "")
        events.append(
            ScheduleEvent(
                title=str(form[f"title_{index}"]),
                date=str(form[f"date_{index}"]),
                start_time=str(form[f"start_time_{index}"]),
                end_time=form.get(f"end_time_{index}") or None,
                description=str(form.get(f"description_{index}") or "") or None,
                location=location_raw or None,
                color_id=str(form.get(f"color_id_{index}") or "") or None,
            )
        )
        index += 1

    try:
        creds = cal_service.get_credentials(
            settings.google_oauth_credentials_path,
            settings.google_token_path,
        )
    except cal_service.NeedsAuthError:
        pending_path = TMP_DIR / f"{session_id}_pending.json"
        pending_path.write_text(json.dumps([ev.model_dump_json() for ev in events]))
        return RedirectResponse(url=f"/auth/start?session_id={session_id}", status_code=303)

    try:
        links = cal_service.push_events(events, creds, settings.google_calendar_id, settings.timezone, notification_minutes)
    except HttpError as exc:
        return templates.TemplateResponse(
            request, "review.html",
            context={
                "schedule": ParsedSchedule(
                    events=events, raw_ocr_text="", source_image_name=""
                ),
                "session_id": session_id,
                "error": f"Google Calendar error: {exc}",
            },
            status_code=502,
        )

    for path in [TMP_DIR / f"{session_id}.json", TMP_DIR / f"{session_id}_pending.json"]:
        if path.exists():
            path.unlink()

    return templates.TemplateResponse(
        request, "success.html",
        context={"links": links, "count": len(events)},
    )
