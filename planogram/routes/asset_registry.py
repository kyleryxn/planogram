from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Adjust these two if you move folders later
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

_template_map = {
    "index": "index.html",
    "calendars": "calendars.html",
    "events": "events.html",
}

_static_map = {
    "main_css": "css/styles.min.css",
    "main_js": "js/app.js",
    "logo": "img/logo.png",
    # add more...
}


def get_template(name: str) -> str:
    try:
        return _template_map[name]
    except KeyError:
        raise ValueError(f"No template mapped for key '{name}'")


def get_static(name: str) -> str:
    try:
        return _static_map[name]
    except KeyError:
        raise ValueError(f"No static asset mapped for key '{name}'")
