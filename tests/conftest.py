"""Shared fixtures for the Planogram test suite."""

import io
from pathlib import Path

from PIL import Image

from planogram.config import Settings


def make_image_bytes(width: int = 100, height: int = 100, fmt: str = "JPEG") -> bytes:
    """Create a minimal in-memory image for upload tests."""
    img = Image.new("RGB", (width, height), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


TEST_SETTINGS = Settings.model_construct(
    anthropic_api_key="sk-ant-test",
    google_oauth_credentials_path=Path("credentials/oauth-client.json"),
    google_token_path=Path("credentials/token.json"),
    google_calendar_id="primary",
    timezone="America/New_York",
    google_maps_api_key="",
    google_oauth_redirect_uri="http://localhost:8080/auth/callback",
)
