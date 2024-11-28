import asyncio
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from typing import Dict, Any, Optional, Tuple, List

from app.models.prediction import Prediction, PredictionOutcome, PredictionComparison
from app.models.match import Match, MatchResult
from app.core.config import settings

class PredictionType:
    DOUBLE_CHANCE = "Double chance"
    COMBO_DOUBLE_CHANCE = "Combo Double chance" 
    WINNER = "Winner"
    COMBO_WINNER = "Combo Winner"

class PredictionEvaluationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_all_predictions(self) -> Dict[str, Any]:
        """Évalue ou met à jour toutes les prédictions terminées."""
        try:
            stats = {
                "total_processed": 0,
                "successful_evaluations": 0,
                "errors": []
            }

            # Sélectionner toutes les prédictions avec leurs relations
            query = (
                select(Prediction, MatchResult, Match)
                .join(Match, Prediction.match_id == Match.id)
                .join(MatchResult, Match.id == MatchResult.match_id)
                .where(Match.status == 'FT')
                .options(
                    selectinload(Prediction.comparison),
                    selectinload(Prediction.teams_data)
                )
            )
            
            result = await self.db.execute(query)
            predictions = result.fetchall()

            # Traitement par lots
            batch_size = 100
            for i in range(0, len(predictions), batch_size):
                batch = predictions[i:i + batch_size]
                for prediction, match_result, match in batch:
                    try:
                        await self._evaluate_single_prediction(prediction, match_result, match)
                        stats["successful_evaluations"] += 1
                    except Exception as e:
                        error_msg = f"Erreur prédiction {prediction.id}: {str(e)}"
                        stats["errors"].append(error_msg)
                        print(error_msg)
                    stats["total_processed"] += 1
                await self.db.commit()

            return stats

        except Exception as e:
            await self.db.rollback()
            print(f"Erreur globale: {str(e)}")
            raise

    async def _evaluate_single_prediction(self, prediction: Prediction, match_result: MatchResult, match: Match) -> None:
        """Évalue une prédiction et met à jour ou crée son outcome."""
        outcome = await self._get_or_create_outcome(prediction.id)
        winner_id, winner_name = self._get_match_winner(match_result, match)

        # Mise à jour de l'outcome
        outcome.updated_at = datetime.now(UTC)
        outcome.both_teams_scored = match_result.home_score > 0 and match_result.away_score > 0
        outcome.winner_prediction_correct = self._is_winner_prediction_correct(
            prediction, winner_id, winner_name
        )

        if prediction.win_or_draw:
            outcome.win_or_draw_prediction_correct = (
                winner_id is None or outcome.winner_prediction_correct
            )

        if prediction.under_over:
            outcome.under_over_prediction_correct = self._is_under_over_correct(
                prediction.under_over, 
                match_result.home_score + match_result.away_score
            )

        # Calcul des métriques
        outcome.goals_prediction_accuracy = self._calculate_goals_accuracy(
            prediction, match_result
        )
        outcome.pre_match_confidence = self._calculate_pre_match_confidence(prediction)
        outcome.form_difference = self._calculate_form_difference(prediction)
        outcome.historical_accuracy = await self._calculate_historical_accuracy(
            self._get_prediction_type(prediction.advice)
        )

    async def _get_or_create_outcome(self, prediction_id: int) -> PredictionOutcome:
        """Récupère l'outcome existant ou en crée un nouveau."""
        query = select(PredictionOutcome).where(
            PredictionOutcome.prediction_id == prediction_id
        )
        result = await self.db.execute(query)
        outcome = result.scalar_one_or_none()
        
        if not outcome:
            outcome = PredictionOutcome(
                prediction_id=prediction_id, 
                created_at=datetime.now(UTC)
            )
            self.db.add(outcome)
        
        return outcome

    def _get_match_winner(self, match_result: MatchResult, match: Match) -> Tuple[Optional[int], Optional[str]]:
        """Détermine l'équipe gagnante du match."""
        if match_result.home_score > match_result.away_score:
            return match.home_team_id, match.home_team
        elif match_result.away_score > match_result.home_score:
            return match.away_team_id, match.away_team
        return None, None

    def _is_winner_prediction_correct(self, prediction: Prediction, winner_id: Optional[int], winner_name: Optional[str]) -> bool:
        """Vérifie si la prédiction du vainqueur est correcte."""
        if winner_id is None:
            return prediction.winner_id is None
        if prediction.winner_id is None:
            return False
        
        return (prediction.winner_id == winner_id or 
                prediction.winner_name == winner_name)

    def _is_under_over_correct(self, prediction: str, total_goals: int) -> bool:
        """Vérifie si la prédiction under/over est correcte."""
        try:
            value, prediction_type = prediction.split()
            threshold = float(value)
            if prediction_type.lower() == "over":
                return total_goals > threshold
            return total_goals < threshold
        except (ValueError, AttributeError):
            return False

    def _calculate_goals_accuracy(self, prediction: Prediction, result: MatchResult) -> float:
        """Calcule la précision de la prédiction des buts (0-100%)."""
        try:
            pred_home = float(prediction.goals_home or 0)
            pred_away = float(prediction.goals_away or 0)
            
            home_diff = abs(pred_home - result.home_score)
            away_diff = abs(pred_away - result.away_score)
            
            max_error = max(result.home_score, result.away_score, 1)
            accuracy = (1 - ((home_diff + away_diff) / (2 * max_error))) * 100
            
            return max(0, min(100, accuracy))
        except (ValueError, ZeroDivisionError):
            return 0

    def _calculate_pre_match_confidence(self, prediction: Prediction) -> float:
        """Calcule le niveau de confiance pré-match (0-100%)."""
        if not prediction.comparison:
            return 0

        weights = {
            'form': 0.25,
            'attack': 0.2,
            'defense': 0.2,
            'h2h': 0.15,
            'poisson': 0.2
        }

        metrics = {
            'form': abs(prediction.comparison.form_home - prediction.comparison.form_away),
            'attack': abs(prediction.comparison.att_home - prediction.comparison.att_away),
            'defense': abs(prediction.comparison.def_home - prediction.comparison.def_away),
            'h2h': abs(prediction.comparison.h2h_home - prediction.comparison.h2h_away),
            'poisson': abs(prediction.comparison.poisson_distribution_home - 
                          prediction.comparison.poisson_distribution_away)
        }

        confidence = sum(metrics[key] * weight for key, weight in weights.items())
        return min(100, max(0, confidence))

    def _calculate_form_difference(self, prediction: Prediction) -> float:
        """Calcule la différence de forme entre les équipes (0-100%)."""
        if not prediction.teams_data or len(prediction.teams_data) != 2:
            return 0

        teams = sorted(prediction.teams_data, key=lambda x: x.is_home)
        return abs(teams[0].last_5_form - teams[1].last_5_form)

    async def _calculate_historical_accuracy(self, prediction_type: str) -> float:
        """Calcule la précision historique pour ce type de prédiction (0-100%)."""
        try:
            query = (
                select(
                    func.count(case((PredictionOutcome.winner_prediction_correct.is_(True), 1))).label('correct'),
                    func.count(PredictionOutcome.id).label('total')
                )
                .join(Prediction)
                .where(Prediction.advice.ilike(f"%{prediction_type}%"))
            )
            
            result = await self.db.execute(query)
            stats = result.first()
            
            if not stats or not stats.total:
                return 0
            
            return (stats.correct / stats.total) * 100
            
        except Exception:
            return 0

    def _get_prediction_type(self, advice: Optional[str]) -> str:
        """Détermine le type de prédiction basé sur l'advice."""
        if not advice:
            return "Unknown"
            
        advice = advice.lower()
        if "double chance" in advice:
            return "Combo Double chance" if "combo" in advice else "Double chance"
        elif "winner" in advice:
            return "Combo Winner" if "combo" in advice else "Winner"
        return "Unknown"

async def main():
    """Point d'entrée principal du script."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        service = PredictionEvaluationService(session)
        try:
            stats = await service.evaluate_all_predictions()
            print("\nStatistiques d'évaluation:")
            print(f"Total traité: {stats['total_processed']}")
            print(f"Évaluations réussies: {stats['successful_evaluations']}")
            if stats['errors']:
                print("\nErreurs rencontrées:")
                for error in stats['errors'][:10]:
                    print(f"- {error}")
                if len(stats['errors']) > 10:
                    print(f"... et {len(stats['errors']) - 10} autres erreurs")
        except Exception as e:
            print(f"Erreur fatale: {str(e)}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
