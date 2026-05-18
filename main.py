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
