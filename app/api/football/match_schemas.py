from pydantic import BaseModel
from typing import List, Optional, Dict, Union, Any

class VenueApi(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    capacity: Optional[int] = None

class StatusApi(BaseModel):
    long: str
    short: str
    elapsed: Optional[int] = None

class FixtureApi(BaseModel):
    id: int
    date: str
    referee: Optional[str] = None
    timezone: str
    timestamp: int
    periods: Dict[str, Optional[int]]
    venue: VenueApi
    status: StatusApi

class TeamApi(BaseModel):
    id: int
    name: str
    logo: Optional[str] = None
    winner: Optional[bool] = None

class TeamsApi(BaseModel):
    home: TeamApi
    away: TeamApi

class GoalsApi(BaseModel):
    home: Optional[int] = None
    away: Optional[int] = None

class LeagueApi(BaseModel):
    id: int
    name: str
    country: str
    logo: Optional[str] = None
    flag: Optional[str] = None
    season: int
    round: Optional[str] = None

class MatchResponse(BaseModel):
    fixture: FixtureApi
    league: LeagueApi
    teams: TeamsApi
    goals: GoalsApi
    events: Optional[List[Dict[str, Any]]] = None
    statistics: Optional[List[Dict[str, Any]]] = None

class ApiResponse(BaseModel):
    get: str
    parameters: Union[Dict[str, Any], List[Any], None] = None
    errors: List[Any] = []
    results: int
    paging: Dict[str, int]
    response: List[MatchResponse]

class MatchSyncResponse(BaseModel):
    total_matches: int
    synced_matches: int
    created_matches: int = 0
    updated_matches: int = 0
    errors: List[str] = []
