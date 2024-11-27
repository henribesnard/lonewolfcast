from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel

from app.db.session import get_db
from app.services.sync.predictions_service import PredictionSyncService
from app.models.match import Match

# Response models
class SyncResponseBase(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

class SyncStatsResponse(BaseModel):
    status: str = "success"
    message: str = "Statistiques récupérées"
    data: Dict[str, Any]

router = APIRouter(prefix="/api/sync")

@router.post("/predictions", response_model=SyncResponseBase)
async def sync_predictions(db: AsyncSession = Depends(get_db)):
    """
    Synchronise les prédictions pour tous les matchs non synchronisés
    """
    try:
        service = PredictionSyncService(db)
        result = await service.sync_predictions()
        
        return {
            "status": "success",
            "message": f"Synchronisation terminée - {result['synced_matches']}/{result['total_matches']} matchs traités",
            "data": {
                "total_matches": result["total_matches"],
                "synced_matches": result["synced_matches"],
                "error_count": len(result["errors"]),
                "errors": result["errors"][:5] if result["errors"] else []
            }
        }
        
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la synchronisation: {str(e)}"
        )

@router.get("/predictions/status", response_model=SyncStatsResponse)
async def get_predictions_status(db: AsyncSession = Depends(get_db)):
    """
    Retourne les statistiques de synchronisation des prédictions
    """
    try:
        query = select(
            func.count(Match.id).label('total'),
            func.sum(case((Match.predictions_synced == True, 1), else_=0)).label('synced'),
            func.max(Match.last_predictions_sync).label('last_sync')
        )
        
        result = await db.execute(query)
        stats = result.first()
        
        total = stats.total or 0
        synced = stats.synced or 0
        last_sync = stats.last_sync.isoformat() if stats.last_sync else None
        
        return {
            "status": "success",
            "message": "Statistiques récupérées avec succès",
            "data": {
                "total_matches": total,
                "synced_matches": synced,
                "pending_matches": total - synced,
                "last_sync": last_sync
            }
        }
        
    except Exception as e:
        print(f"Erreur lors de la récupération des stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des stats: {str(e)}"
        )

@router.post("/predictions/{match_id}", response_model=SyncResponseBase)
async def sync_single_prediction(match_id: int, db: AsyncSession = Depends(get_db)):
    """
    Synchronise les prédictions pour un match spécifique
    """
    try:
        service = PredictionSyncService(db)
        
        query = select(Match).where(Match.id == match_id)
        result = await db.execute(query)
        match = result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} non trouvé")
        
        success = await service.sync_single_match(match)
        
        return {
            "status": "success" if success else "warning",
            "message": "Prédictions synchronisées" if success else "Aucune prédiction disponible",
            "data": {
                "match_id": match_id,
                "synced": success
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la synchronisation du match {match_id}: {str(e)}"
        )