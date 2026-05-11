"""FastAPI Web API for the Daily Activity Management System."""

import os
import secrets
import logging

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .routers import auth, activities, categories, habits, journals, stats, pomodoro, goals, backup, dashboard, health
from .deps import UPLOAD_DIR, JOURNAL_IMG_DIR

logger = logging.getLogger(__name__)

app = FastAPI(title="Daily Activity Management System")

# Session middleware — use SECRET_KEY env var or generate a random one
_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    _secret_key = secrets.token_hex(32)
    logger.warning("SECRET_KEY not set — using a random key. Sessions will not survive restarts. Set SECRET_KEY env var for production.")

app.add_middleware(
    SessionMiddleware,
    secret_key=_secret_key,
)

# Include routers
app.include_router(auth.router)
app.include_router(activities.router)
app.include_router(categories.router)
app.include_router(habits.router)
app.include_router(journals.router)
app.include_router(stats.router)
app.include_router(pomodoro.router)
app.include_router(goals.router)
app.include_router(backup.router)
app.include_router(dashboard.router)
app.include_router(health.router)
app.include_router(activities.template_router)
app.include_router(activities.tag_router)

# Static file mounts
_pkg_dir = os.path.dirname(os.path.abspath(__file__))

# Mount uploads directories
app.mount("/uploads/avatars", StaticFiles(directory=UPLOAD_DIR), name="avatars")
app.mount("/uploads/journals", StaticFiles(directory=JOURNAL_IMG_DIR), name="journal_images")

# Mount Vue static assets — serve at /assets/ to match Vite default base path
_vue_dir = os.path.join(_pkg_dir, "static", "vue")
if os.path.isdir(_vue_dir):
    _vue_assets = os.path.join(_vue_dir, "assets")
    if os.path.isdir(_vue_assets):
        app.mount("/assets", StaticFiles(directory=_vue_assets), name="vue_assets")


# Serve Vue public files (favicon, icons, etc.)
@app.get("/favicon.svg")
def favicon():
    path = os.path.join(_vue_dir, "favicon.svg")
    if os.path.exists(path):
        return FileResponse(path, media_type="image/svg+xml")

@app.get("/icons.svg")
def icons():
    path = os.path.join(_vue_dir, "icons.svg")
    if os.path.exists(path):
        return FileResponse(path, media_type="image/svg+xml")

# Templates
_template_dir = os.path.join(_pkg_dir, "templates")
templates = Jinja2Templates(directory=_template_dir)


@app.get("/login")
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
def register_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/")
def index(request: Request):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    vue_index = os.path.join(_pkg_dir, "static", "vue", "index.html")
    if os.path.exists(vue_index):
        return FileResponse(vue_index)
    return templates.TemplateResponse("index.html", {"request": request})


def run_server(host="0.0.0.0", port=5000, debug=False):
    import uvicorn
    uvicorn.run(
        "daily_activity_manager.api:app",
        host=host,
        port=port,
        reload=debug,
    )


if __name__ == "__main__":
    run_server(debug=True)
