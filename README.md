# Planogram

Upload a photo of a printed or handwritten schedule and push the events directly to Google Calendar.

## How it works

1. Upload a schedule image (JPG, PNG, WEBP, or PDF)
2. [Google Cloud Vision](https://cloud.google.com/vision) extracts the text via OCR
3. [Claude](https://anthropic.com) (claude-sonnet-4-6) parses the raw text into structured events
4. Review and edit the parsed events before confirming
5. Events are pushed to your Google Calendar

## Requirements

- Python 3.14+
- [Poetry](https://python-poetry.org/)
- A Google Cloud project with **Cloud Vision API** and **Google Calendar API** enabled
- An [Anthropic API key](https://console.anthropic.com)

## Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Google Cloud setup

#### Cloud Vision (OCR)
1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create or select a project
2. Enable the **Cloud Vision API**
3. Create a service account: **APIs & Services → Credentials → Create Credentials → Service Account**
4. Grant it the role **Cloud Vision API User**
5. Create a JSON key and download it to `credentials/vision-service-account.json`

#### Google Calendar (event push)
1. Enable the **Google Calendar API** in the same project
2. Create an OAuth client: **APIs & Services → Credentials → Create Credentials → OAuth client ID**
   - Application type: **Web application**
   - Authorized redirect URI: `http://127.0.0.1:8080/auth/callback`
3. Download the JSON and save it to `credentials/oauth-client.json`
4. In **APIs & Services → OAuth consent screen**, add your Google account as a test user

### 3. Environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_VISION_CREDENTIALS_PATH=credentials/vision-service-account.json
GOOGLE_OAUTH_CREDENTIALS_PATH=credentials/oauth-client.json
GOOGLE_TOKEN_PATH=credentials/token.json
GOOGLE_CALENDAR_ID=primary
TIMEZONE=America/New_York
```

## Running

```bash
poetry run uvicorn main:app --reload --port 8080
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080).

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
│   │   ├── vision.py                # Google Cloud Vision OCR
│   │   ├── parser.py                # Claude API event extraction
│   │   └── calendar.py             # Google Calendar OAuth + push
│   ├── routes/
│   │   ├── upload.py                # GET /, POST /upload
│   │   ├── review.py                # GET /review, POST /confirm
│   │   └── auth.py                  # GET /auth/start, /auth/callback
│   └── templates/                   # Jinja2 HTML templates
├── static/
│   ├── style.scss                   # SCSS entry point
│   ├── style.css                    # Compiled CSS (do not edit directly)
│   ├── abstracts/                   # Variables
│   ├── base/                        # Reset, base styles
│   ├── components/                  # Buttons, alerts, forms, table
│   ├── layout/                      # Header
│   └── pages/                       # Upload, review, success page styles
├── credentials/                     # GCP keys — gitignored
├── tmp/                             # Session state files — gitignored
└── .env                             # Secrets — gitignored
```

## License

[GPL-3.0](./LICENSE)
