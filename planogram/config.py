"""Application configuration loaded from environment variables and .env.

Settings are validated at startup via pydantic-settings.  All values can be
overridden by setting the corresponding environment variable or adding it to a
``.env`` file in the project root.
"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings populated from environment variables or .env.

    Attributes:
        anthropic_api_key: Secret key for the Anthropic Claude API.
        google_oauth_credentials_path: Path to the Google OAuth 2.0 client
            secrets JSON file downloaded from Google Cloud Console.
        google_token_path: Path where the user's OAuth token is persisted after
            the first successful authorization.
        google_calendar_id: Google Calendar to push events to.  Defaults to the
            authenticated user's primary calendar.
        timezone: IANA timezone name used when creating calendar events.
        google_maps_api_key: Optional Maps API key that enables place
            autocomplete suggestions on the review form.
        google_oauth_redirect_uri: Redirect URI registered in the Google Cloud
            Console OAuth client configuration.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str = Field(default="")
    google_oauth_credentials_path: Path = Path("credentials/oauth-client.json")
    google_token_path: Path = Path("credentials/token.json")
    google_calendar_id: str = "primary"
    timezone: str = "America/New_York"
    google_maps_api_key: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8080/auth/callback"

    @field_validator("anthropic_api_key")
    @classmethod
    def api_key_must_be_set(cls, v: str) -> str:
        """Ensure the Anthropic API key is present.

        Args:
            v: The raw value read from the environment.

        Returns:
            The validated API key string.

        Raises:
            ValueError: If the key is empty or not set.
        """
        if not v:
            raise ValueError("ANTHROPIC_API_KEY must be set in .env")
        return v


def get_settings() -> Settings:
    """Instantiate and return application settings.

    Reads from environment variables and the ``.env`` file in the project root.
    Called once per request; consider wrapping with ``functools.lru_cache`` if
    startup latency becomes a concern.

    Returns:
        A fully validated ``Settings`` instance.

    Raises:
        ValidationError: If any required setting is missing or invalid.
    """
    return Settings()
