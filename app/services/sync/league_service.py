from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from app.api.football.league_client import FootballAPIClient
from app.api.football.league_schemas import ApiResponse, LeagueSyncResponse
from app.models.league import League, Season
from app.services.apiRate_limiter_service import ApiRateLimiter
from app.core.config import settings
import asyncio


class LeagueSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = FootballAPIClient()
        # Rate limiter pour la limite journalière
        self.daily_limiter = ApiRateLimiter(settings.API_MAX_CALLS_PER_DAY, db)
        # Pour la limite par minute
        self.minute_calls = 0
        self.minute_start = datetime.now()

    async def _check_minute_limit(self):
        """Vérifie et gère la limite par minute"""
        current_time = datetime.now()
        
        if current_time - self.minute_start >= timedelta(minutes=1):
            # Nouvelle minute commence
            print(f"Réinitialisation du compteur minute: {self.minute_calls} appels effectués")
            self.minute_calls = 0
            self.minute_start = current_time
        
        if self.minute_calls >= settings.API_RATE_LIMIT:
            # Attendre jusqu'à la prochaine minute
            seconds_to_wait = 60 - (current_time - self.minute_start).seconds
            print(f"Limite par minute atteinte ({settings.API_RATE_LIMIT}), attente de {seconds_to_wait} secondes")
            await asyncio.sleep(seconds_to_wait)  # Utilisation d'asyncio.sleep
            self.minute_calls = 0
            self.minute_start = datetime.now()
        
        self.minute_calls += 1
        print(f"Appels cette minute: {self.minute_calls}/{settings.API_RATE_LIMIT}")

    async def _make_api_call(self):
        """Fait un appel API en respectant les deux limites"""
        try:
            # Vérifier la limite journalière
            if not await self.daily_limiter.can_make_call():
                raise Exception(f"Limite d'appels API journalière atteinte ({settings.API_MAX_CALLS_PER_DAY}). Réessayez demain.")

            # Vérifier la limite par minute
            await self._check_minute_limit()

            # Enregistrer l'appel dans le compteur journalier
            await self.daily_limiter.record_call()
            
            # Faire l'appel API
            return await self.client.get_leagues()
        except Exception as e:
            print(f"Erreur lors de l'appel API: {str(e)}")
            raise

    async def get_dashboard_stats(self) -> dict:
        """
        Récupère les statistiques pour le dashboard
        """
        try:
            print("\n=== Début récupération des stats dashboard ===")

            # Compter les leagues avec prédictions
            count_query = select(func.count(distinct(League.id))).select_from(League).join(
                Season,
                (League.id == Season.league_id) & (Season.has_predictions.is_(True))
            )
            count_result = await self.db.execute(count_query)
            leagues_count = count_result.scalar_one_or_none() or 0
            print(f"\nNombre total de leagues avec prédictions: {leagues_count}")

            # Récupérer la dernière mise à jour
            update_query = select(func.max(League.updated_at)).select_from(League)
            update_result = await self.db.execute(update_query)
            last_sync = update_result.scalar_one_or_none()
            print(f"\nDernière mise à jour (raw): {last_sync}")

            formatted_date = "Jamais"
            if last_sync:
                try:
                    formatted_date = last_sync.strftime("%d/%m/%Y %H:%M:%S")
                    print(f"Date formatée: {formatted_date}")
                except Exception as e:
                    print(f"Erreur lors du formatage de la date: {str(e)}")
                    formatted_date = "Erreur format"

            # Récupérer les stats d'utilisation API
            today = datetime.now().date()
            api_usage = await self.daily_limiter._get_usage_from_db(today)
            if api_usage:
                print(f"\nUtilisation API aujourd'hui: {api_usage.calls_made}/{settings.API_MAX_CALLS_PER_DAY}")

            print("\n=== Fin récupération des stats dashboard ===")
            return {
                "leagues_count": leagues_count,
                "last_sync": formatted_date
            }

        except Exception as e:
            print(f"\nErreur dans get_dashboard_stats: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                "leagues_count": 0,
                "last_sync": "Non disponible"
            }

    async def sync_leagues(self) -> LeagueSyncResponse:
        """
        Synchronise toutes les leagues depuis l'API
        """
        try:
            print("\n=== Début synchronisation des leagues ===")
            current_time = datetime.utcnow()
            print(f"Timestamp de synchronisation: {current_time}")

            # Appel API avec gestion des limites
            print("Récupération des données via l'API...")
            api_data = await self._make_api_call()
            api_response = ApiResponse(**api_data)

            # Afficher les stats d'utilisation API
            today = datetime.now().date()
            daily_usage = await self.daily_limiter._get_usage_from_db(today)
            if daily_usage:
                print(f"Utilisation API aujourd'hui: {daily_usage.calls_made}/{settings.API_MAX_CALLS_PER_DAY}")

            total_leagues = len(api_response.response)
            synced_leagues = 0
            synced_seasons = 0
            created_leagues = 0
            updated_leagues = 0
            errors = []

            print(f"\nTraitement de {total_leagues} leagues...")

            for league_data in api_response.response:
                try:
                    stmt = select(League).where(League.api_id == league_data.league.id)
                    result = await self.db.execute(stmt)
                    db_league = result.scalar_one_or_none()

                    if db_league:
                        db_league.name = league_data.league.name
                        db_league.country = league_data.country.name
                        db_league.logo = league_data.league.logo
                        db_league.flag = league_data.country.flag
                        db_league.type = league_data.league.type
                        db_league.updated_at = current_time
                        updated_leagues += 1
                        print(f"Mise à jour league: {db_league.name}")
                    else:
                        db_league = League(
                            api_id=league_data.league.id,
                            name=league_data.league.name,
                            country=league_data.country.name,
                            logo=league_data.league.logo,
                            flag=league_data.country.flag,
                            type=league_data.league.type,
                            created_at=current_time,
                            updated_at=current_time
                        )
                        self.db.add(db_league)
                        created_leagues += 1
                        print(f"Création league: {db_league.name}")

                    await self.db.flush()

                    for season_data in league_data.seasons:
                        try:
                            stmt = select(Season).where(
                                Season.league_id == db_league.id,
                                Season.year == season_data.year
                            )
                            result = await self.db.execute(stmt)
                            db_season = result.scalar_one_or_none()

                            if db_season:
                                db_season.current = season_data.current
                                db_season.has_predictions = season_data.coverage.predictions
                                db_season.has_odds = season_data.coverage.odds
                                db_season.updated_at = current_time
                                print(f"Mise à jour saison {season_data.year} pour {db_league.name}")
                            else:
                                db_season = Season(
                                    league_id=db_league.id,
                                    year=season_data.year,
                                    start_date=datetime.strptime(season_data.start, "%Y-%m-%d"),
                                    end_date=datetime.strptime(season_data.end, "%Y-%m-%d"),
                                    current=season_data.current,
                                    has_predictions=season_data.coverage.predictions,
                                    has_odds=season_data.coverage.odds,
                                    created_at=current_time,
                                    updated_at=current_time
                                )
                                self.db.add(db_season)
                                print(f"Création saison {season_data.year} pour {db_league.name}")

                            synced_seasons += 1

                        except Exception as e:
                            error_msg = f"Erreur traitement saison {season_data.year} pour league {db_league.name}: {str(e)}"
                            print(error_msg)
                            errors.append(error_msg)
                            continue

                    synced_leagues += 1
                    await self.db.commit()

                except Exception as e:
                    await self.db.rollback()
                    error_msg = f"Erreur traitement league {league_data.league.name}: {str(e)}"
                    print(error_msg)
                    errors.append(error_msg)
                    continue

            print("\n=== Fin synchronisation des leagues ===")
            
            # Stats finales d'utilisation API
            final_usage = await self.daily_limiter._get_usage_from_db(today)
            if final_usage:
                print(f"Utilisation API finale: {final_usage.calls_made}/{settings.API_MAX_CALLS_PER_DAY}")

            return LeagueSyncResponse(
                total_leagues=total_leagues,
                synced_leagues=synced_leagues,
                total_seasons=total_leagues * len(api_response.response[0].seasons),
                synced_seasons=synced_seasons,
                created_leagues=created_leagues,
                updated_leagues=updated_leagues,
                errors=errors
            )

        except Exception as e:
            print(f"\nErreur lors de la synchronisation: {str(e)}")
            raise Exception(f"Erreur lors de la synchronisation: {str(e)}")