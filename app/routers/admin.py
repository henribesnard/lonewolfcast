import os
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader, Environment
from app.services.sync.league_service import LeagueSyncService
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.api_usage import ApiUsage
from app.core.config import settings

router = APIRouter(prefix="/admin")
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin", "templates")

# Créer l'environnement Jinja2 avec les dossiers de template
env = Environment(
    loader=FileSystemLoader([
        template_dir,
        os.path.join(template_dir, "components")
    ])
)

# Utiliser seulement l'environnement personnalisé
templates = Jinja2Templates(env=env)

@router.get("/", name="admin.dashboard")
@router.get("", name="admin.dashboard")
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    service = LeagueSyncService(db)
    try:
        # Récupérer les statistiques du tableau de bord
        stats = await service.get_dashboard_stats()

        # Récupérer les statistiques d'utilisation des appels API
        today = datetime.now().date()
        stmt = select(ApiUsage.calls_made).where(ApiUsage.date == today)
        result = await db.execute(stmt)
        calls_made_today = result.scalar_one_or_none() or 0
        max_calls_per_day = settings.API_MAX_CALLS_PER_DAY

        # Passer toutes les variables au template
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "leagues_count": stats["leagues_count"],
                "last_sync": stats["last_sync"],
                "calls_made_today": calls_made_today,
                "max_calls_per_day": max_calls_per_day
            }
        )
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "leagues_count": 0,
                "last_sync": "Non disponible",
                "calls_made_today": 0,
                "max_calls_per_day": settings.API_MAX_CALLS_PER_DAY
            }
        )
