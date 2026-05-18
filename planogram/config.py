from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str
    google_oauth_credentials_path: Path = Path("credentials/oauth-client.json")
    google_token_path: Path = Path("credentials/token.json")
    google_calendar_id: str = "primary"
    timezone: str = "America/Chicago"
    google_maps_api_key: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8080/auth/callback"


def get_settings() -> Settings:
    return Settings()
