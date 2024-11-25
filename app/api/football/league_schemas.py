from pydantic import BaseModel
from typing import List, Optional, Dict, Union, Any

class FixtureCoverage(BaseModel):
    events: bool = False
    lineups: bool = False
    statistics_fixtures: bool = False
    statistics_players: bool = False

class Coverage(BaseModel):
    fixtures: FixtureCoverage
    standings: bool = False
    players: bool = False
    top_scorers: bool = False
    top_assists: bool = False
    top_cards: bool = False
    injuries: bool = False
    predictions: bool = False
    odds: bool = False

class SeasonApi(BaseModel):
    year: int
    start: str
    end: str
    current: bool
    coverage: Coverage

class CountryApi(BaseModel):
    name: str
    code: Optional[str] = None
    flag: Optional[str] = None

class LeagueApi(BaseModel):
    id: int
    name: str
    type: str
    logo: Optional[str] = None

class LeagueResponse(BaseModel):
    league: LeagueApi
    country: CountryApi
    seasons: List[SeasonApi]

class ApiResponse(BaseModel):
    get: str
    parameters: Union[Dict[str, Any], List[Any], None] = None
    errors: List[Any] = []
    results: int
    paging: Dict[str, int]
    response: List[LeagueResponse]

class LeagueSyncResponse(BaseModel):
    total_leagues: int
    synced_leagues: int
    total_seasons: int
    synced_seasons: int
    created_leagues: int = 0
    updated_leagues: int = 0
    errors: List[str] = []