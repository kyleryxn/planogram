from __future__ import annotations

from typing import Tuple

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from planogram.config import SCOPES, REDIRECT_URI, CREDENTIALS_PATH
from planogram.google_oauth.token_store import save_flow, pop_flow, get_user_creds


def build_auth_flow() -> Flow:
    # Use the Web client JSON; its root key should be "web"
    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_PATH),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    return flow


def start_authorization() -> Tuple[str, str]:
    flow = build_auth_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",  # ensures refresh_token on the first run
    )
    save_flow(state, flow)

    return auth_url, state


def finish_authorization(state: str, authorization_response_url: str) -> Credentials:
    flow = pop_flow(state)

    if not flow:
        raise ValueError("Invalid or expired OAuth state")

    flow.fetch_token(authorization_response=authorization_response_url)
    creds: Credentials = flow.credentials

    return creds


def get_calendar_service_for(user_key: str):
    creds = get_user_creds(user_key)

    if not creds:
        raise PermissionError("User is not authorized with Google")

    # google-auth will auto-refresh if refresh_token is present
    return build("calendar", "v3", credentials=creds)
