from __future__ import annotations

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession

from planogram.google_oauth.token_repo import get_user_creds_db, save_user_creds_db


async def get_calendar_service_for(db: AsyncSession, user_key: str):
    creds = await get_user_creds_db(db, user_key)

    if not creds:
        raise PermissionError("User is not authorized with Google")

    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        await save_user_creds_db(db, user_key, creds)

    return build("calendar", "v3", credentials=creds)
