from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

TOKENS_DIR = Path(__file__).resolve().parent.parent / "tokens"
TOKENS_DIR.mkdir(parents=True, exist_ok=True)

# Stores pending Flow objects until callback (keyed by 'state')
_pending_flows: Dict[str, Flow] = {}

# Stores user creds by a simple user key (replace with a real user id/session id)
_user_creds: Dict[str, Credentials] = {}


def save_flow(state: str, flow: Flow) -> None:
    _pending_flows[state] = flow


def pop_flow(state: str) -> Optional[Flow]:
    return _pending_flows.pop(state, None)


def _token_path(user_key: str) -> Path:
    return TOKENS_DIR / f"google_{user_key}.json"


def save_user_creds(user_key: str, creds: Credentials) -> None:
    _user_creds[user_key] = creds


def get_user_creds(user_key: str) -> Optional[Credentials]:
    path = _token_path(user_key)

    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Credentials.from_authorized_user_info(data)
    except Exception:
        return None
