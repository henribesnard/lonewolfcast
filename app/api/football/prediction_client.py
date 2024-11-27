from typing import Dict, Any
import httpx
from app.core.config import settings
import json

class PredictionAPIClient:
    def __init__(self):
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-apisports-key": settings.API_KEY, 
        }

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Méthode générique pour faire des requêtes à l'API"""
        print(f"Making request to {endpoint} with params: {params}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/{endpoint}",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )
                response.raise_for_status()

                try:
                    data = response.json()
                    print(f"Response status: {response.status_code}")
                    print(f"Response contains {len(data.get('response', []))} items")
                    return data
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {str(e)}")
                    print(f"Response content: {response.content}")
                    raise Exception("Invalid JSON response from API")

            except httpx.HTTPError as e:
                print(f"HTTP Error: {str(e)}")
                raise Exception(f"Error fetching data from API: {str(e)}")

    async def get_predictions(self, fixture_id: int) -> Dict[str, Any]:
        """
        Récupère les prédictions pour un match spécifique.
        Args:
            fixture_id: ID du match pour lequel récupérer les prédictions.
        Returns:
            Dict contenant la réponse de l'API.
        """
        params = {"fixture": fixture_id}

        try:
            print(f"Fetching predictions for fixture {fixture_id}...")
            data = await self._make_request("predictions", params)
            print(f"Successfully fetched predictions for fixture {fixture_id}")
            return data
        except Exception as e:
            print(f"Error in get_predictions: {str(e)}")
            raise Exception(f"Error fetching predictions: {str(e)}")
