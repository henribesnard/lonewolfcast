from typing import Dict, Any
import httpx
from app.core.config import settings
import json

class MatchAPIClient:
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
                    timeout=30.0
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

    async def get_matches(self, league_id: int, season: int) -> Dict[str, Any]:
        """
        Récupère les matchs pour une league et une saison données
        Args:
            league_id: ID de la league
            season: Année de la saison
        Returns:
            Dict contenant la réponse de l'API
        """
        params = {
            "league": league_id,
            "season": season
        }

        try:
            print(f"Fetching matches for league {league_id} and season {season}...")
            data = await self._make_request("fixtures", params)
            print(f"Successfully fetched {data.get('results', 0)} matches")
            return data
        except Exception as e:
            print(f"Error in get_matches: {str(e)}")
            raise Exception(f"Error fetching matches: {str(e)}")
