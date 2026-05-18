# Planogram

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Upload a photo of a printed or handwritten schedule and push the events directly to Google Calendar.

## How it works

1. Upload a schedule image (JPG, PNG, WEBP, or PDF)
2. [Claude](https://anthropic.com) (claude-opus-4-7) reads the image and transcribes every shift column by column
3. A second Claude pass (claude-sonnet-4-6) converts the transcription into structured calendar events
4. Review and edit the parsed events before confirming
5. Events are pushed to your Google Calendar

## Requirements

- Python 3.14+
- [Poetry](https://python-poetry.org/)
- A Google Cloud project with the **Google Calendar API** enabled
- An [Anthropic API key](https://console.anthropic.com)

## Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Google Cloud setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create or select a project
2. Enable the **Google Calendar API**
3. Create an OAuth client: **APIs & Services → Credentials → Create Credentials → OAuth client ID**
   - Application type: **Web application**
   - Authorized redirect URI: `http://localhost:8080/auth/callback`
4. Download the JSON and save it to `credentials/oauth-client.json`
5. In **APIs & Services → OAuth consent screen**, add your Google account as a test user with the `calendar.events` scope

### 3. Environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
ANTHROPIC_API_KEY=sk-ant...
GOOGLE_MAPS_API_KEY=AI...
GOOGLE_OAUTH_CREDENTIALS_PATH=credentials/oauth-client.json
GOOGLE_TOKEN_PATH=credentials/token.json
GOOGLE_CALENDAR_ID=primary
TIMEZONE=America/New_York
```

## Running

```bash
poetry run uvicorn main:app --reload --port 8080
```

Open [http://localhost:8080](http://localhost:8080).

The first time you push events to Google Calendar, you'll be redirected through an OAuth consent screen. 
After approving, the token is saved to `credentials/token.json` and later runs skip the auth step.

## Project structure

```
planogram/
├── main.py                          # FastAPI app entry point
├── planogram/
│   ├── config.py                    # Settings loaded from .env
│   ├── models.py                    # ScheduleEvent, ParsedSchedule
│   ├── services/
│   │   ├── parser.py                # Two-pass Claude image → events pipeline
│   │   └── calendar.py              # Google Calendar OAuth + push
│   ├── routes/
│   │   ├── upload.py                # GET /, POST /upload
│   │   ├── review.py                # GET /review, POST /confirm
│   │   └── auth.py                  # GET /auth/start, /auth/callback
│   └── templates/                   # Jinja2 HTML templates
├── static/
│   ├── css/
│   │   ├── style.scss               # SCSS entry point
│   │   ├── style.min.css            # Compiled CSS (do not edit directly)
│   │   ├── abstracts/               # Variables
│   │   ├── base/                    # Reset, base styles, dark mode
│   │   ├── components/              # Buttons, alerts, forms, table
│   │   ├── layout/                  # Header, footer
│   │   └── pages/                   # Upload, review, success page styles
│   └── js/
│       ├── upload.js / upload.min.js
│       └── review.js / review.min.js
├── credentials/                     # GCP keys — gitignored
├── tmp/                             # Session state files — gitignored
└── .env                             # Secrets — gitignored
```

## License

[GPL-3.0](./LICENSE)
