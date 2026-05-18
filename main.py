"""Planogram FastAPI application entry point.

Mounts the static file directory and registers the upload, review, and auth
routers.  The OAUTHLIB_INSECURE_TRANSPORT environment variable is set to allow
the Google OAuth redirect over plain HTTP during local development — remove or
guard this for any internet-facing deployment.

Run with:
    uvicorn main:app --reload --port 8080
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from planogram.routes import auth, review, upload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_logger = logging.getLogger(__name__)
_TMP_DIR = Path("tmp")
_SESSION_MAX_AGE = 24 * 3600  # seconds


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Delete session files older than 24 hours on startup."""
    removed = 0
    if _TMP_DIR.exists():
        cutoff = time.time() - _SESSION_MAX_AGE
        for f in _TMP_DIR.glob("*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink(missing_ok=True)
                removed += 1
    if removed:
        _logger.info("Cleaned up %d expired session file(s)", removed)
    yield


# Allow OAuth over plain HTTP for local development
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

app = FastAPI(title="Planogram", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(upload.router)
app.include_router(review.router)
app.include_router(auth.router)
