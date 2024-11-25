from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.sync.match_service import MatchSyncService
from app.api.football.match_schemas import MatchSyncResponse

router = APIRouter(prefix="/api/sync")


@router.post("/matches", response_model=MatchSyncResponse)
async def sync_matches(db: AsyncSession = Depends(get_db)):
    """
    Endpoint pour synchroniser les matchs
    """
    try:
        service = MatchSyncService(db)
        result = await service.sync_matches()
        return result
    except Exception as e:
        print(f"Sync Error: {str(e)}")  # Log l'erreur côté serveur
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
