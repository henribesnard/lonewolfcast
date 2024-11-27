from datetime import datetime
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.match import Match

async def get_dashboard_stats(db: AsyncSession) -> dict:
    """
    Récupère toutes les statistiques pour le dashboard
    """
    try:
        # Stats des matchs
        total_matches_query = select(func.count(Match.id))
        result = await db.execute(total_matches_query)
        total_matches = result.scalar_one() or 0

        # Stats des matchs par status
        ft_query = select(func.count(Match.id)).where(Match.status == 'FT')
        result = await db.execute(ft_query)
        ft_matches = result.scalar_one() or 0

        ns_query = select(func.count(Match.id)).where(Match.status == 'NS')
        result = await db.execute(ns_query)
        ns_matches = result.scalar_one() or 0

        # Stats des prédictions
        synced_query = select(func.count(Match.id)).where(Match.predictions_synced == True)
        result = await db.execute(synced_query)
        synced_matches = result.scalar_one() or 0

        pending_matches = total_matches - synced_matches

        # Dates de dernière mise à jour
        matches_update_query = select(func.max(Match.updated_at))
        result = await db.execute(matches_update_query)
        matches_last_sync = result.scalar_one_or_none()
        
        predictions_update_query = select(func.max(Match.last_predictions_sync))
        result = await db.execute(predictions_update_query)
        predictions_last_sync = result.scalar_one_or_none()
        
        # Formater les dates
        matches_formatted_date = matches_last_sync.strftime("%d/%m/%Y %H:%M:%S") if matches_last_sync else "Jamais"
        predictions_formatted_date = predictions_last_sync.strftime("%d/%m/%Y %H:%M:%S") if predictions_last_sync else "Jamais"

        return {
            # Stats des matchs
            "total_matches": total_matches,
            "match_status": {
                "Terminés": {
                    "count": ft_matches,
                    "percentage": round((ft_matches/total_matches*100), 1) if total_matches > 0 else 0
                },
                "À venir": {
                    "count": ns_matches,
                    "percentage": round((ns_matches/total_matches*100), 1) if total_matches > 0 else 0
                }
            },
            "matches_last_sync": matches_formatted_date,
            
            # Stats des prédictions
            "total_predictions": total_matches,
            "predictions_status": {
                "Synchronisés": {
                    "count": synced_matches,
                    "percentage": round((synced_matches/total_matches*100), 1) if total_matches > 0 else 0
                },
                "En attente": {
                    "count": pending_matches,
                    "percentage": round((pending_matches/total_matches*100), 1) if total_matches > 0 else 0
                }
            },
            "predictions_last_sync": predictions_formatted_date
        }

    except Exception as e:
        print(f"Erreur lors de la récupération des stats: {str(e)}")
        return {
            "total_matches": 0,
            "match_status": {
                "Terminés": {"count": 0, "percentage": 0},
                "À venir": {"count": 0, "percentage": 0}
            },
            "matches_last_sync": "Non disponible",
            "total_predictions": 0,
            "predictions_status": {
                "Synchronisés": {"count": 0, "percentage": 0},
                "En attente": {"count": 0, "percentage": 0}
            },
            "predictions_last_sync": "Non disponible"
        }
