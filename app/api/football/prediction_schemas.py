from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class PredictionWinner(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    comment: Optional[str] = None

class PredictionGoals(BaseModel):
    home: Optional[str] = None
    away: Optional[str] = None

class PredictionPercent(BaseModel):
    home: str  # ex: "0%"
    draw: str  # ex: "50%"
    away: str  # ex: "50%"

class TeamGoals(BaseModel):
    total: int
    average: str  # ex: "0.0"

class LastFiveGoals(BaseModel):
    for_: TeamGoals = Field(..., alias="for")
    against: TeamGoals

class LastFiveStats(BaseModel):
    played: int
    form: str  # ex: "0%"
    att: str  # ex: "0%"
    def_: str = Field(..., alias="def")  # ex: "0%"
    goals: LastFiveGoals

class LeagueFixtures(BaseModel):
    played: Dict[str, int]  # home, away, total
    wins: Dict[str, int]
    draws: Dict[str, int]
    loses: Dict[str, int]

class GoalsMinuteStats(BaseModel):
    total: Optional[int] = None
    percentage: Optional[str] = None

class UnderOver(BaseModel):
    over: int
    under: int

class GoalsStats(BaseModel):
    total: Dict[str, int]  # home, away, total
    average: Dict[str, str]  # home, away, total
    minute: Dict[str, GoalsMinuteStats]
    under_over: Dict[str, UnderOver]  # Ajout du type spécifique

class BiggestStreak(BaseModel):
    wins: int
    draws: int
    loses: int

class BiggestScores(BaseModel):
    home: Optional[str] = None
    away: Optional[str] = None

class BiggestGoals(BaseModel):
    for_: Dict[str, int] = Field(..., alias="for")
    against: Dict[str, int]

class BiggestStats(BaseModel):
    streak: BiggestStreak
    wins: BiggestScores
    loses: BiggestScores
    goals: BiggestGoals

class LineupInfo(BaseModel):
    formation: str
    played: int

class CardStats(BaseModel):
    total: Optional[int] = None
    percentage: Optional[str] = None

class PenaltyStats(BaseModel):
    scored: Dict[str, str]  # total et percentage
    missed: Dict[str, str]
    total: int

class LeagueStats(BaseModel):
    form: str  # ex: "LLLLL"
    fixtures: LeagueFixtures
    goals: GoalsStats
    biggest: BiggestStats
    clean_sheet: Dict[str, int]
    failed_to_score: Dict[str, int]
    penalty: PenaltyStats
    lineups: List[LineupInfo]
    cards: Dict[str, Dict[str, CardStats]]  # yellow, red et leurs périodes

class PredictionTeamData(BaseModel):
    id: int
    name: str
    logo: str
    last_5: LastFiveStats
    league: LeagueStats

class PredictionComparison(BaseModel):
    form: Dict[str, str]  # home, away
    att: Dict[str, str]
    def_: Dict[str, str] = Field(..., alias="def")
    poisson_distribution: Dict[str, str]
    h2h: Dict[str, str]
    goals: Dict[str, str]
    total: Dict[str, str]

class LeagueInfo(BaseModel):
    id: int
    name: str
    country: str
    logo: str
    flag: Optional[str] = None
    season: int

class PredictionData(BaseModel):
    winner: PredictionWinner
    win_or_draw: bool
    under_over: Optional[str] = None
    goals: PredictionGoals
    advice: str
    percent: PredictionPercent

class H2HTeams(BaseModel):
    home: Dict[str, Any]
    away: Dict[str, Any]

class H2HFixture(BaseModel):
    id: int
    referee: Optional[str]
    timezone: str
    date: str
    timestamp: int
    periods: Dict[str, int]
    venue: Dict[str, Any]
    status: Dict[str, Any]

class H2HMatch(BaseModel):
    fixture: H2HFixture
    league: LeagueInfo
    teams: H2HTeams
    goals: Dict[str, int]
    score: Dict[str, Dict[str, Optional[int]]]

class PredictionResponse(BaseModel):
    predictions: PredictionData
    league: LeagueInfo
    teams: Dict[str, PredictionTeamData]
    comparison: PredictionComparison
    h2h: List[H2HMatch]

class PredictionApiResponse(BaseModel):
    get: str
    parameters: Dict[str, Any]
    errors: List[Any]
    results: int
    paging: Dict[str, int]
    response: List[PredictionResponse]