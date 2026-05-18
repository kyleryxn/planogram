import io
import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from PIL import Image

from planogram.config import get_settings
from planogram.models import ParsedSchedule
from planogram.services import parser

MAX_IMAGE_PX = 1568

MEDIA_TYPE_MAP = {
    "jpeg": "image/jpeg",
    "jpg":  "image/jpeg",
    "png":  "image/png",
    "gif":  "image/gif",
    "webp": "image/webp",
}

router = APIRouter()
templates = Jinja2Templates(directory="planogram/templates")
TMP_DIR = Path("tmp")


def _resize(image_bytes: bytes) -> tuple[bytes, str]:
    with Image.open(io.BytesIO(image_bytes)) as img:
        img.thumbnail((MAX_IMAGE_PX, MAX_IMAGE_PX), Image.LANCZOS)
        fmt = (img.format or "JPEG").lower()
        buf = io.BytesIO()
        img.save(buf, format=fmt.upper())
        media_type = MEDIA_TYPE_MAP.get(fmt, "image/jpeg")
        return buf.getvalue(), media_type


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.post("/upload")
async def upload(
    request: Request,
    file: UploadFile = File(...),
    person_name: str = Form(default=""),
):
    settings = get_settings()

    image_bytes = await file.read()
    if not image_bytes:
        return templates.TemplateResponse(
            request, "index.html",
            context={"error": "Uploaded file is empty."},
            status_code=400,
        )

    try:
        image_bytes, media_type = _resize(image_bytes)
    except Exception as exc:
        return templates.TemplateResponse(
            request, "index.html",
            context={"error": f"Could not process image: {exc}"},
            status_code=422,
        )

    try:
        events, raw_response = parser.parse_events(
            image_bytes,
            media_type,
            settings.anthropic_api_key,
            date.today().isoformat(),
            person_name=person_name.strip() or None,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request, "index.html",
            context={"error": f"Event parsing failed: {exc}"},
            status_code=422,
        )

    schedule = ParsedSchedule(
        events=events,
        raw_ocr_text=raw_response,
        source_image_name=file.filename or "unknown",
    )

    TMP_DIR.mkdir(exist_ok=True)
    session_id = str(uuid.uuid4())
    (TMP_DIR / f"{session_id}.json").write_text(schedule.model_dump_json())

    return RedirectResponse(url=f"/review?id={session_id}", status_code=303)
