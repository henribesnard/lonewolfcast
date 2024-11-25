from datetime import datetime, timedelta
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.api_usage import ApiUsage

class ApiRateLimiter:
    def __init__(self, max_calls_per_day: int, db: AsyncSession):
        """
        Initialise le limiteur d'appels API.

        :param max_calls_per_day: Limite d'appels API par jour
        :param db: Session de base de données
        """
        self.max_calls_per_day = max_calls_per_day  # Limite quotidienne
        self.db = db  # Session de base de données
        self.calls_made_today = 0  # Nombre d'appels effectués aujourd'hui
        self.reset_time = self._calculate_next_reset_time()  # Heure de réinitialisation

    def _calculate_next_reset_time(self):
        """
        Calcule la prochaine réinitialisation (minuit).
        
        :return: Heure de la prochaine réinitialisation
        """
        now = datetime.now()
        next_reset = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return next_reset

    async def _get_usage_from_db(self, today):
        """
        Récupère les données d'utilisation API pour la date actuelle depuis la base.

        :param today: Date actuelle
        :return: Objet ApiUsage ou None
        """
        stmt = select(ApiUsage).where(ApiUsage.date == today)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _save_usage_to_db(self, today):
        """
        Crée une nouvelle entrée pour l'utilisation API.

        :param today: Date actuelle
        """
        new_usage = ApiUsage(date=today, calls_made=0, reset_time=self.reset_time)
        self.db.add(new_usage)
        await self.db.commit()

    async def _update_usage(self, today):
        """
        Met à jour le nombre d'appels effectués aujourd'hui.

        :param today: Date actuelle
        """
        stmt = (
            update(ApiUsage)
            .where(ApiUsage.date == today)
            .values(calls_made=self.calls_made_today)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def can_make_call(self) -> bool:
        """
        Vérifie si un appel API peut être effectué en respectant les limites.

        :return: True si un appel peut être effectué, False sinon
        """
        today = datetime.now().date()
        usage = await self._get_usage_from_db(today)

        if usage:
            self.calls_made_today = usage.calls_made
        else:
            # Initialiser une nouvelle entrée pour aujourd'hui si elle n'existe pas
            self.calls_made_today = 0
            await self._save_usage_to_db(today)

        return self.calls_made_today < self.max_calls_per_day

    async def record_call(self):
        """
        Enregistre un appel API effectué.
        """
        today = datetime.now().date()

        # Vérifie si un appel peut être effectué
        if await self.can_make_call():
            self.calls_made_today += 1
            await self._update_usage(today)  # Mise à jour de la base
        else:
            raise Exception("Limite d'appels API atteinte pour aujourd'hui.")

    async def reset_limits(self):
        """
        Réinitialise les limites quotidiennes (à minuit).
        """
        today = datetime.now().date()
        self.calls_made_today = 0
        self.reset_time = self._calculate_next_reset_time()
        await self._save_usage_to_db(today)  # Réinitialiser dans la base
