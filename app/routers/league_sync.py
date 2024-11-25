from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.sync.league_service import LeagueSyncService
from app.api.football.league_schemas import LeagueSyncResponse

router = APIRouter(prefix="/api/sync")

@router.post("/leagues")
async def sync_leagues(db: AsyncSession = Depends(get_db)):
    try:
        service = LeagueSyncService(db)
        result = await service.sync_leagues()
        return result
    except Exception as e:
        print(f"Sync Error: {str(e)}")  # Log l'erreur côté serveur
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )