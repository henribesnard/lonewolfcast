from pydantic import BaseModel
from typing import List, Optional, Dict, Union, Any

# Définition du lieu (venue)
class VenueApi(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None

# Statut du match
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
    periods: Optional[Dict[str, Optional[int]]] = None
    venue: Optional[VenueApi] = None
    status: StatusApi
    round: Optional[str] = None

# Information sur une équipe
class TeamApi(BaseModel):
    id: int
    name: str
    logo: Optional[str] = None
    winner: Optional[bool] = None

# Equipes (domicile et extérieur)
class TeamsApi(BaseModel):
    home: TeamApi
    away: TeamApi

# Nombre de buts
class GoalsApi(BaseModel):
    home: Optional[int] = None
    away: Optional[int] = None

# Informations sur la ligue
class LeagueApi(BaseModel):
    id: int
    name: str
    country: str
    logo: Optional[str] = None
    flag: Optional[str] = None
    season: int
    round: Optional[str] = None

# Réponse pour un match
class MatchResponse(BaseModel):
    fixture: FixtureApi
    league: LeagueApi
    teams: TeamsApi
    goals: GoalsApi
    score: Optional[Dict[str, Any]] = None

# Réponse globale de l'API
class ApiResponse(BaseModel):
    get: str
    parameters: Union[Dict[str, Any], List[Any], None] = None
    errors: List[Any] = []
    results: int
    paging: Dict[str, int]
    response: List[MatchResponse]

# Réponse pour la synchronisation des matchs
class MatchSyncResponse(BaseModel):
    total_matches: int
    synced_matches: int
    created_matches: int = 0
    updated_matches: int = 0
    errors: List[str] = []
