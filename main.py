from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.core.config import Settings
from app.routers import admin, league_sync, match_sync
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

# Configuration
settings = Settings()
app = FastAPI(title=settings.APP_NAME)

# Utiliser le même BASE_DIR que dans config.py
BASE_DIR = Path(__file__).parent
print(f"\nApplication Paths:")
print(f"===============================")
print(f"BASE_DIR: {BASE_DIR}")

# Utiliser les chemins depuis settings
templates_dir = settings.TEMPLATES_DIR
print(f"\nTemplates Configuration:")
print(f"===============================")
print(f"TEMPLATES_DIR: {templates_dir}")
print(f"Templates directory exists: {os.path.exists(templates_dir)}")
print(f"Templates files: {os.listdir(templates_dir) if os.path.exists(templates_dir) else 'Directory not found'}")

templates = Jinja2Templates(directory=templates_dir)

# Static files setup - utiliser le chemin des settings
static_dir = settings.STATIC_DIR
print(f"\nStatic Files Configuration:")
print(f"===============================")
print(f"STATIC_DIR: {static_dir}")
print(f"Static directory exists: {os.path.exists(static_dir)}")
print(f"Static files: {os.listdir(static_dir) if os.path.exists(static_dir) else 'Directory not found'}")

# Mount static files
app.mount(
    "/admin/static",
    StaticFiles(directory=static_dir),
    name="admin-static"
)

# Routes
@app.get("/")
async def root():
    return RedirectResponse(url="/admin")

# Include routers
app.include_router(admin.router)
app.include_router(league_sync.router)
app.include_router(match_sync.router)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    print(f"404 Error - Looking for template: {os.path.join(templates_dir, '404.html')}")
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    print(f"500 Error - Looking for template: {os.path.join(templates_dir, 'error.html')}")
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_code": 500,
            "error_message": "Erreur serveur",
            "error_description": str(exc)
        },
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)