from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from google.oauth2.credentials import Credentials
from sqlalchemy.ext.asyncio import AsyncSession

from planogram.models.google_token import GoogleToken


def creds_to_dict(creds: Credentials) -> dict:
    # google-auth Credentials.to_json() gives a JSON string with all fields we need
    return json.loads(creds.to_json())


def dict_to_creds(data: dict) -> Credentials:
    return Credentials.from_authorized_user_info(data)


async def save_user_creds_db(db: AsyncSession, user_key: str, creds: Credentials) -> None:
    data = creds_to_dict(creds)
    refresh_token = data.get("refresh_token")
    expiry_str = data.get("expiry")
    expiry = None

    if expiry_str:
        # google uses ISO8601; handle trailing Z
        expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))

    row = await db.get(GoogleToken, user_key)

    if row is None:
        row = GoogleToken(
            user_key=user_key,
            auth_json=json.dumps(data),
            refresh_token=refresh_token,
            expiry=expiry,
        )
        db.add(row)
    else:
        row.auth_json = json.dumps(data)
        row.refresh_token = refresh_token
        row.expiry = expiry

    await db.commit()


async def get_user_creds_db(db: AsyncSession, user_key: str) -> Optional[Credentials]:
    row = await db.get(GoogleToken, user_key)

    if not row:
        return None

    return dict_to_creds(json.loads(row.auth_json))
