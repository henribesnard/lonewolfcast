from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.football.match_client import MatchAPIClient
from app.api.football.match_schemas import ApiResponse, MatchSyncResponse
from app.models.match import Match
from app.models.league import League, Season


class MatchSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = MatchAPIClient()

    async def sync_matches(self) -> MatchSyncResponse:
        """
        Synchronise tous les matchs pour les couples league-saison disponibles en base
        """
        try:
            print("\n=== Début synchronisation des matchs ===")
            current_time = datetime.utcnow()
            print(f"Timestamp de synchronisation : {current_time}")

            # Récupérer les couples league-saison à synchroniser
            league_season_query = (
                select(League.api_id, Season.year)
                .join(Season, League.id == Season.league_id)
                .where(Season.has_predictions.is_(True))
            )
            result = await self.db.execute(league_season_query)
            league_season_pairs = result.fetchall()

            total_matches = 0
            synced_matches = 0
            created_matches = 0
            updated_matches = 0
            errors = []

            print(f"\nTraitement de {len(league_season_pairs)} couples league-saison...")

            for league_id, season in league_season_pairs:
                try:
                    print(f"\nSynchronisation pour league {league_id}, saison {season}...")
                    api_data = await self.client.get_matches(league_id=league_id, season=season)
                    api_response = ApiResponse(**api_data)

                    for match_data in api_response.response:
                        fixture = match_data["fixture"]
                        teams = match_data["teams"]
                        league = match_data["league"]

                        # Vérifier si le match existe déjà
                        stmt = select(Match).where(Match.api_fixture_id == fixture["id"])
                        result = await self.db.execute(stmt)
                        db_match = result.scalar_one_or_none()

                        if db_match:
                            # Mise à jour du match existant
                            db_match.date = fixture["date"]
                            db_match.status = fixture["status"]["short"]
                            db_match.home_team = teams["home"]["name"]
                            db_match.away_team = teams["away"]["name"]
                            db_match.updated_at = current_time
                            updated_matches += 1
                            print(f"Mise à jour du match {fixture['id']}")
                        else:
                            # Création d'un nouveau match
                            db_match = Match(
                                api_fixture_id=fixture["id"],
                                league_id=league_id,
                                date=fixture["date"],
                                status=fixture["status"]["short"],
                                home_team=teams["home"]["name"],
                                home_team_id=teams["home"]["id"],
                                home_team_logo=teams["home"]["logo"],
                                away_team=teams["away"]["name"],
                                away_team_id=teams["away"]["id"],
                                away_team_logo=teams["away"]["logo"],
                                venue=fixture["venue"]["name"],
                                round=league["round"],
                                created_at=current_time,
                                updated_at=current_time
                            )
                            self.db.add(db_match)
                            created_matches += 1
                            print(f"Création du match {fixture['id']}")

                        synced_matches += 1

                    # Valider les changements après chaque league-saison
                    await self.db.commit()

                except Exception as e:
                    # Annuler les modifications en cas d'erreur
                    await self.db.rollback()
                    error_msg = f"Erreur lors de la synchronisation pour league={league_id}, saison={season}: {str(e)}"
                    print(error_msg)
                    errors.append(error_msg)
                    continue

            print("\n=== Fin synchronisation des matchs ===")
            return MatchSyncResponse(
                total_matches=total_matches,
                synced_matches=synced_matches,
                created_matches=created_matches,
                updated_matches=updated_matches,
                errors=errors
            )

        except Exception as e:
            print(f"\nErreur globale lors de la synchronisation des matchs: {str(e)}")
            raise Exception(f"Erreur globale lors de la synchronisation des matchs: {str(e)}")
