from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from planogram.database import get_async_session
from planogram.google_oauth.client import start_authorization, finish_authorization
from planogram.google_oauth.token_repo import save_user_creds_db

router = APIRouter(prefix="/auth", tags=["auth"])

# For demo purposes, one “user” across the app.
# Replace with your real session/user id.
DEMO_USER_KEY = "demo-user"


@router.get("/start")
def auth_start():
    auth_url, _state = start_authorization()
    return RedirectResponse(auth_url)


@router.get("/callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(get_async_session),):
    # Handle user-cancel/error from Google
    if err := request.query_params.get("error"):
        raise HTTPException(status_code=400, detail=f"OAuth error from Google: {err}")

    state = request.query_params.get("state")
    if not state:
        raise HTTPException(status_code=400, detail="Missing state")

    try:
        # finish_authorization(state, current_url) -> creds
        creds = finish_authorization(state, str(request.url))

        # Persist under whichever app-level key you want
        await save_user_creds_db(db, DEMO_USER_KEY, creds)
        return PlainTextResponse("Google authorization complete.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e}")
