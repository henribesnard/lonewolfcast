import os
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader, Environment
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.matches_stats_services import get_dashboard_stats
from app.core.config import settings

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
    try:
        # Récupérer toutes les statistiques
        dashboard_stats = await get_dashboard_stats(db)

        template_data = {
            "request": request,
            **dashboard_stats  # Déployer toutes les stats
        }

        print("Template data:", template_data)  # Pour debug
        return templates.TemplateResponse("dashboard.html", template_data)
        
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "total_matches": 0,
                "match_status": {},
                "matches_last_sync": "Non disponible",
                "total_predictions": 0,
                "predictions_status": {},
                "predictions_last_sync": "Non disponible"
            }
        )
