"""Planogram FastAPI application entry point.

Mounts the static file directory and registers the upload, review, and auth
routers.  The OAUTHLIB_INSECURE_TRANSPORT environment variable is set to allow
the Google OAuth redirect over plain HTTP during local development — remove or
guard this for any internet-facing deployment.

Run with:
    uvicorn main:app --reload --port 8080
"""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from planogram.routes import auth, review, upload

# Allow OAuth over plain HTTP for local development
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

app = FastAPI(title="Planogram")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(upload.router)
app.include_router(review.router)
app.include_router(auth.router)
