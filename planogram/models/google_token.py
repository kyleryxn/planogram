from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime


class Base(DeclarativeBase):
    pass


class GoogleToken(Base):
    __tablename__ = "google_tokens"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)

    # Store the full google-auth JSON for maximum compatibility
    # (token, refresh_token, token_uri, client_id, client_secret, scopes, expiry)
    auth_json: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional convenience fields (helpful for debugging/ops)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
