"""Upload route — schedule image ingestion and AI parsing.

Exposes two endpoints:

- ``GET /`` renders the upload form.
- ``POST /upload`` receives the image, resizes it if necessary, runs the
  two-pass Claude parsing pipeline, persists the result as a temporary JSON
  session file, and redirects to the review page.
"""

import io
import logging
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

logger = logging.getLogger(__name__)

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


def resize(image_bytes: bytes) -> tuple[bytes, str]:
    """Resize an image so neither dimension exceeds ``MAX_IMAGE_PX`` pixels.

    Uses Pillow's ``thumbnail`` method which preserves aspect ratio and only
    shrinks — images smaller than the limit are left at their original size.

    Args:
        image_bytes: Raw bytes of the uploaded image file.

    Returns:
        A tuple of ``(resized_bytes, media_type)`` where ``media_type`` is the
        MIME type string inferred from the image format.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img.thumbnail((MAX_IMAGE_PX, MAX_IMAGE_PX), Image.LANCZOS)
        fmt = (img.format or "JPEG").lower()
        buf = io.BytesIO()
        img.save(buf, format=fmt.upper())
        media_type = MEDIA_TYPE_MAP.get(fmt, "image/jpeg")
        return buf.getvalue(), media_type


@router.get("/")
async def index(request: Request):
    """Render the schedule upload form.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        An HTML response rendering ``index.html``.
    """
    return templates.TemplateResponse(request, "index.html")


@router.post("/upload")
async def upload(
    request: Request,
    file: UploadFile = File(...),
    person_name: str = Form(default=""),
):
    """Process an uploaded schedule image and redirect to the review page.

    Reads the uploaded file, resizes it to fit within ``MAX_IMAGE_PX`` on each
    side, runs the two-pass Claude parsing pipeline, and stores the resulting
    ``ParsedSchedule`` as a UUID-named JSON file in ``tmp/``.  On success,
    redirects the browser to ``/review?id=<uuid>``.

    Args:
        request: The incoming FastAPI request object.
        file: The multipart-uploaded schedule image (JPEG, PNG, WEBP, or PDF).
        person_name: Optional name used to filter a multi-person schedule down
            to a single individual's shifts.

    Returns:
        A 303 redirect to the review page on success, or a re-rendered upload
        form with an error message on failure.
    """
    settings = get_settings()

    image_bytes = await file.read()
    logger.info("Upload received: %r (%d bytes)", file.filename, len(image_bytes))

    if not image_bytes:
        logger.warning("Upload rejected: empty file")
        return templates.TemplateResponse(
            request, "index.html",
            context={"error": "Uploaded file is empty."},
            status_code=400,
        )

    try:
        image_bytes, media_type = resize(image_bytes)
    except Exception as exc:
        logger.warning("Image processing failed: %s", exc)
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
        logger.warning("Parsing failed: %s", exc)
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
    logger.info("Session %s created with %d event(s)", session_id, len(events))

    return RedirectResponse(url=f"/review?id={session_id}", status_code=303)
