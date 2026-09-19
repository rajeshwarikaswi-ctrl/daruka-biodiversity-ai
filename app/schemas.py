from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

TimeHorizon = Literal["short", "medium", "long"]

class LandContext(BaseModel):
    soil_organic_carbon_pct: Optional[float] = None
    soil_ph: Optional[float] = None
    soil_moisture: Optional[float] = None
    rainfall_mm_annual: Optional[float] = None
    temperature_c_avg: Optional[float] = None
    land_use: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    species_richness: Optional[int] = None
    pollution_index: Optional[float] = None
    deforestation_rate_pct: Optional[float] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[LandContext] = None

class Recommendation(BaseModel):
    action: str
    rationale: str
    impacted_metrics: List[str]
    time_horizon: TimeHorizon
    expected_effect: str
    references: List[str]
    confidence: float = Field(ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    clarifying_questions: List[str] = []
    recommendations: List[Recommendation] = []
    retrieved_evidence: List[Dict[str, Any]] = []
    missing_metrics: List[str] = []
    metrics_snapshot: Dict[str, Any] = {}
