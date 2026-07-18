"""Type definitions for StadiumIQ."""
from typing import TypedDict, Optional, List, Dict, Any

class ZoneData(TypedDict):
    name: str
    occupancy: int
    capacity: int
    percentage: float
    level: str
    inflow: int
    outflow: int

class ChatResult(TypedDict):
    response: str
    intent: str
    confidence: float
    language: str
    fan_id: str
    sentiment: Optional[Dict[str, Any]]

class IncidentData(TypedDict):
    id: str
    type: str
    status: str
    severity: str
    location: Dict[str, Any]
    details: str
    created_at: float

class MatchEvent(TypedDict):
    type: str
    minute: int
    team: str
    player: str
    description: str

class SatisfactionScore(TypedDict):
    touchpoint: str
    score: float
    fan_id: Optional[str]
    timestamp: float

class KPIData(TypedDict):
    total_occupancy: int
    capacity: int
    occupancy_pct: float
    active_incidents: int
    safety_score: float
    sentiment_avg: float
    fan_count: int
    revenue: float

class NavigationRoute(TypedDict):
    origin: str
    destination: str
    distance: str
    time: str
    steps: List[str]
    accessible: bool
