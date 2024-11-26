from datetime import datetime
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.match import Match

async def get_match_stats(db: AsyncSession) -> dict:
    """
    Récupère les statistiques des matchs avec focus sur FT et NS
    """
    try:
        # Total des matchs
        total_query = select(func.count(Match.id))
        result = await db.execute(total_query)
        total_matches = result.scalar_one() or 0

        # Compter les matchs FT
        ft_query = select(func.count(Match.id)).where(Match.status == 'FT')
        result = await db.execute(ft_query)
        ft_matches = result.scalar_one() or 0

        # Compter les matchs NS
        ns_query = select(func.count(Match.id)).where(Match.status == 'NS')
        result = await db.execute(ns_query)
        ns_matches = result.scalar_one() or 0

        # Dernière mise à jour
        update_query = select(func.max(Match.updated_at))
        result = await db.execute(update_query)
        last_sync = result.scalar_one_or_none()
        
        formatted_date = "Jamais"
        if last_sync:
            formatted_date = last_sync.strftime("%d/%m/%Y %H:%M:%S")

        # Préparer les stats avec labels plus descriptifs
        status_counts = {
            "Terminés": {
                "count": ft_matches,
                "percentage": round((ft_matches/total_matches*100), 1) if total_matches > 0 else 0
            },
            "À venir": {
                "count": ns_matches,
                "percentage": round((ns_matches/total_matches*100), 1) if total_matches > 0 else 0
            }
        }

        return {
            "total_matches": total_matches,
            "match_status": status_counts,
            "last_sync": formatted_date
        }

    except Exception as e:
        print(f"Erreur lors de la récupération des stats matchs: {str(e)}")
        return {
            "total_matches": 0,
            "match_status": {
                "Terminés": {"count": 0, "percentage": 0},
                "À venir": {"count": 0, "percentage": 0}
            },
            "last_sync": "Non disponible"
        }