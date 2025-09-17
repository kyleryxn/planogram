from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from planogram.routes.asset_registry import TEMPLATES_DIR, get_template, get_static

router = APIRouter(prefix="", tags=["home", "index"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Build URL with url_for('static', path=...)
    main_css_url = request.url_for("static", path=get_static("main_css"))

    return templates.TemplateResponse(
        get_template("index"),
        {
            "request": request,
            "title": "Planogram",
            "main_css_url": main_css_url,
        },
    )
