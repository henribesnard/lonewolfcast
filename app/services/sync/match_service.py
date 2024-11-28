from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.api.football.match_client import MatchAPIClient
from app.api.football.match_schemas import ApiResponse, MatchSyncResponse
from app.models.match import Match, MatchResult
from app.models.league import League, Season

class MatchSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = MatchAPIClient()

    def parse_date(self, date_str: str) -> datetime:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

    async def sync_matches(self) -> MatchSyncResponse:
        try:
            current_time = datetime.utcnow()

            result = await self.db.execute(
                select(League.api_id, League.id)
                .where(League.is_active.is_(True))
            )
            leagues_map = {league.api_id: league.id for league in result.fetchall()}
            
            if not leagues_map:
                raise Exception("Aucune league en base. Synchronisez d'abord les leagues.")

            league_season_query = (
                select(League.api_id, League.id, Season.id, Season.year)
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

            for league_api_id, league_id, season_id, season_year in league_season_pairs:
                try:
                    api_data = await self.client.get_matches(league_id=league_api_id, season=season_year)
                    api_response = ApiResponse(**api_data)

                    for match_data in api_response.response:
                        fixture = match_data.fixture
                        teams = match_data.teams
                        goals = match_data.goals
                        score = match_data.score

                        match_date = self.parse_date(fixture.date)
                        
                        stmt = select(Match).where(Match.api_fixture_id == fixture.id)
                        result = await self.db.execute(stmt)
                        db_match = result.scalar_one_or_none()

                        if db_match:
                            db_match.date = match_date
                            db_match.status = fixture.status.short
                            db_match.home_team = teams.home.name
                            db_match.away_team = teams.away.name
                            db_match.round = match_data.league.round
                            db_match.updated_at = current_time
                            updated_matches += 1

                            if fixture.status.short == "FT":
                                result_stmt = select(MatchResult).where(MatchResult.match_id == db_match.id)
                                result_obj = await self.db.execute(result_stmt)
                                match_result = result_obj.scalar_one_or_none()

                                if match_result:
                                    match_result.home_score = goals.home or 0
                                    match_result.away_score = goals.away or 0
                                else:
                                    match_result = MatchResult(
                                        match_id=db_match.id,
                                        home_score=goals.home or 0,
                                        away_score=goals.away or 0
                                    )
                                    self.db.add(match_result)
                        else:
                            new_match = Match(
                                api_fixture_id=fixture.id,
                                league_id=league_id,
                                date=match_date,
                                status=fixture.status.short,
                                home_team=teams.home.name,
                                home_team_id=teams.home.id,
                                home_team_logo=teams.home.logo,
                                away_team=teams.away.name,
                                away_team_id=teams.away.id,
                                away_team_logo=teams.away.logo,
                                venue=fixture.venue.name if fixture.venue else None,
                                round=match_data.league.round,
                                created_at=current_time,
                                updated_at=current_time
                            )
                            self.db.add(new_match)
                            created_matches += 1

                            if fixture.status.short == "FT":
                                await self.db.flush()
                                match_result = MatchResult(
                                    match_id=new_match.id,
                                    home_score=goals.home or 0,
                                    away_score=goals.away or 0
                                )
                                self.db.add(match_result)

                        await self.db.commit()
                        synced_matches += 1
                        total_matches += 1

                    await self.db.execute(
                        update(Season)
                        .where(Season.id == season_id)
                        .values(matches_synced=True, last_match_sync=current_time)
                    )
                    await self.db.commit()

                except Exception as e:
                    await self.db.rollback()
                    error_msg = f"Erreur pour league={league_api_id}, season={season_year}: {str(e)}"
                    print(error_msg)
                    errors.append(error_msg)

            return MatchSyncResponse(
                total_matches=total_matches,
                synced_matches=synced_matches,
                created_matches=created_matches,
                updated_matches=updated_matches,
                errors=errors
            )

        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Erreur globale: {str(e)}")