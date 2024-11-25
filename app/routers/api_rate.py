from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.db.session import get_db
from sqlalchemy import select
from app.models.api_usage import ApiUsage
from app.core.config import settings
from pydantic import BaseModel

class ApiUsageStats(BaseModel):
    calls_made_today: int
    max_calls_per_day: int

router = APIRouter()

@router.get(
    "/usage-stats",
    response_model=ApiUsageStats,
    summary="Récupère les statistiques d'utilisation des appels API",
)
async def get_api_usage_stats(db: AsyncSession = Depends(get_db)):
    """
    Récupère les statistiques d'utilisation des appels API pour aujourd'hui.
    """
    today = datetime.now().date()
    stmt = select(ApiUsage.calls_made).where(ApiUsage.date == today)

    try:
        result = await db.execute(stmt)
        calls_made_today = result.scalar_one_or_none() or 0
        max_calls_per_day = settings.API_MAX_CALLS_PER_DAY
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")

    return {"calls_made_today": calls_made_today, "max_calls_per_day": max_calls_per_day}
