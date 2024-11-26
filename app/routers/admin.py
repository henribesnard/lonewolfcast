import os
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader, Environment
from app.services.sync.league_service import LeagueSyncService
from app.services.matches_stats_services import get_match_stats
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
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
    league_service = LeagueSyncService(db)
    try:
        # Récupérer les statistiques
        league_stats = await league_service.get_dashboard_stats()
        match_stats = await get_match_stats(db)

        # Combiner toutes les données pour le template
        template_data = {
            "request": request,
            "leagues_count": league_stats["leagues_count"],
            "last_sync": league_stats["last_sync"],
            "total_matches": match_stats["total_matches"],
            "match_status": match_stats["match_status"],
            "matches_last_sync": match_stats["last_sync"]
        }

        print("Template data:", template_data)  # Pour debug

        return templates.TemplateResponse(
            "dashboard.html",
            template_data
        )
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        import traceback
        traceback.print_exc()  # Pour plus de détails sur l'erreur
        
        # Données par défaut en cas d'erreur
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "leagues_count": 0,
                "last_sync": "Non disponible",
                "total_matches": 0,
                "match_status": {},
                "matches_last_sync": "Non disponible"
            }
        )