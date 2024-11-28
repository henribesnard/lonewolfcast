import os
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader, Environment
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.matches_stats_services import get_dashboard_stats
from app.services.sync.league_service import LeagueSyncService

router = APIRouter(prefix="/admin")
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin", "templates")

# Créer l'environnement Jinja2
env = Environment(
    loader=FileSystemLoader([
        template_dir,
        os.path.join(template_dir, "components")
    ])
)

templates = Jinja2Templates(env=env)


@router.get("/", name="admin.dashboard")
@router.get("", name="admin.dashboard")
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Route du tableau de bord admin : affiche les statistiques des matchs et des leagues.
    """
    try:
        # Récupérer les statistiques des matchs
        match_stats = await get_dashboard_stats(db)

        # Récupérer les statistiques des leagues
        league_service = LeagueSyncService(db)
        league_stats = await league_service.get_dashboard_stats_league()

        # Ajouter les statistiques des leagues aux données du template
        template_data = {
            "request": request,
            **match_stats,
            **league_stats,  # Inclut leagues_count et last_sync
        }

        print("Template data:", template_data)  # Debugging
        return templates.TemplateResponse("dashboard.html", template_data)

    except Exception as e:
        print(f"Erreur dans la route dashboard : {str(e)}")
        import traceback
        traceback.print_exc()

        # Retourner une réponse par défaut en cas d'erreur
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "total_matches": 0,
                "match_status": {},
                "matches_last_sync": "Non disponible",
                "total_predictions": 0,
                "predictions_status": {},
                "predictions_last_sync": "Non disponible",
                "leagues_count": 0,
                "last_sync": "Non disponible"
            }
        )
