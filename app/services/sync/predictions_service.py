from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List

from app.models.match import Match
from app.models.prediction import (
    Prediction, PredictionTeam, PredictionComparison, PredictionOutcome
)
from app.api.football.prediction_client import PredictionAPIClient

class PredictionSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = PredictionAPIClient()

    async def _save_prediction(self, match_id: int, prediction_data: Dict[str, Any]) -> bool:
        """Sauvegarde les données de prédiction en base"""
        try:
            predictions = prediction_data['predictions']
            teams = prediction_data['teams']
            comparison = prediction_data['comparison']

            # Créer la nouvelle prédiction
            new_prediction = Prediction(
                match_id=match_id,
                winner_id=predictions['winner'].get('id'),
                winner_name=predictions['winner'].get('name'),
                winner_comment=predictions['winner'].get('comment'),
                win_or_draw=predictions.get('win_or_draw', False),
                under_over=predictions.get('under_over'),
                goals_home=predictions['goals'].get('home'),
                goals_away=predictions['goals'].get('away'),
                advice=predictions.get('advice'),
                percent_home=float(predictions['percent']['home'].rstrip('%')),
                percent_draw=float(predictions['percent']['draw'].rstrip('%')),
                percent_away=float(predictions['percent']['away'].rstrip('%'))
            )
            self.db.add(new_prediction)
            await self.db.flush()

            # Ajouter les équipes
            for side, team_data in teams.items():
                team = PredictionTeam(
                    prediction_id=new_prediction.id,
                    is_home=(side == 'home'),
                    team_id=team_data['id'],
                    team_name=team_data['name'],
                    team_logo=team_data['logo'],
                    last_5_played=team_data['last_5']['played'],
                    last_5_form=float(team_data['last_5']['form'].rstrip('%')),
                    last_5_att=float(team_data['last_5']['att'].rstrip('%')),
                    last_5_def=float(team_data['last_5']['def'].rstrip('%')),
                    goals_for_total=team_data['last_5']['goals']['for']['total'],
                    goals_for_avg=float(team_data['last_5']['goals']['for']['average']),
                    goals_against_total=team_data['last_5']['goals']['against']['total'],
                    goals_against_avg=float(team_data['last_5']['goals']['against']['average']),
                    league_form=team_data['league']['form'],
                    clean_sheet_total=team_data['league']['clean_sheet']['total'],
                    failed_to_score_total=team_data['league']['failed_to_score']['total']
                )
                self.db.add(team)

            # Ajouter la comparaison
            comp = PredictionComparison(
                prediction_id=new_prediction.id,
                form_home=float(comparison['form']['home'].rstrip('%')),
                form_away=float(comparison['form']['away'].rstrip('%')),
                att_home=float(comparison['att']['home'].rstrip('%')),
                att_away=float(comparison['att']['away'].rstrip('%')),
                def_home=float(comparison['def']['home'].rstrip('%')),
                def_away=float(comparison['def']['away'].rstrip('%')),
                poisson_distribution_home=float(comparison['poisson_distribution']['home'].rstrip('%')),
                poisson_distribution_away=float(comparison['poisson_distribution']['away'].rstrip('%')),
                h2h_home=float(comparison['h2h']['home'].rstrip('%')),
                h2h_away=float(comparison['h2h']['away'].rstrip('%')),
                goals_home=float(comparison['goals']['home'].rstrip('%')),
                goals_away=float(comparison['goals']['away'].rstrip('%')),
                total_home=float(comparison['total']['home'].rstrip('%')),
                total_away=float(comparison['total']['away'].rstrip('%'))
            )
            self.db.add(comp)

            # Ajouter l'outcome initial
            outcome = PredictionOutcome(
                prediction_id=new_prediction.id,
                pre_match_confidence=float(comparison['total']['home'].rstrip('%'))
            )
            self.db.add(outcome)

            return True

        except Exception as e:
            print(f"Erreur sauvegarde prédiction: {str(e)}")
            raise

    async def sync_predictions(self) -> Dict[str, Any]:
        """Synchronise les prédictions pour tous les matchs non synchronisés"""
        try:
            # Récupérer les matchs non synchronisés
            query = select(Match).where(Match.predictions_synced == False)
            result = await self.db.execute(query)
            matches_to_sync = result.scalars().all()

            total_matches = len(matches_to_sync)
            synced_matches = 0
            errors: List[str] = []

            print(f"Début synchronisation pour {total_matches} matchs")

            for match in matches_to_sync:
                try:
                    print(f"Synchro match {match.api_fixture_id}")
                    response = await self.client.get_predictions(match.api_fixture_id)
                    
                    if response['response']:
                        await self._save_prediction(match.id, response['response'][0])
                        match.predictions_synced = True
                        match.last_predictions_sync = datetime.utcnow()
                        synced_matches += 1
                        await self.db.commit()
                        print(f"Match {match.api_fixture_id} sync ok")
                    
                except Exception as e:
                    await self.db.rollback()
                    error_msg = f"Erreur match {match.api_fixture_id}: {str(e)}"
                    print(error_msg)
                    errors.append(error_msg)
                    continue

            return {
                "total_matches": total_matches,
                "synced_matches": synced_matches,
                "errors": errors
            }

        except Exception as e:
            await self.db.rollback()
            print(f"Erreur globale: {str(e)}")
            raise

    async def sync_single_match(self, match: Match) -> bool:
        """Synchronise les prédictions pour un match spécifique"""
        try:
            response = await self.client.get_predictions(match.api_fixture_id)
            if response['response']:
                await self._save_prediction(match.id, response['response'][0])
                match.predictions_synced = True
                match.last_predictions_sync = datetime.utcnow()
                await self.db.commit()
                return True
            return False
            
        except Exception as e:
            await self.db.rollback()
            print(f"Erreur sync match {match.api_fixture_id}: {str(e)}")
            raise