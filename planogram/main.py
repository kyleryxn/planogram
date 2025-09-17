from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from planogram.routes import auth, home, calendar
from planogram.routes.asset_registry import STATIC_DIR

app = FastAPI(title="Planogram")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(home.router)
app.include_router(auth.router)
app.include_router(calendar.router)
