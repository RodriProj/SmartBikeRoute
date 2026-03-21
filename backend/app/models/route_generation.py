from pydantic import BaseModel
from typing import Literal, Optional


class RouteGenerationRequest(BaseModel):
    startLat: float
    startLon: float
    endLat: float
    endLon: float
    profile_type: Literal["lazer", "exercicio", "competicao"]
    target_distance_km: Optional[float] = None
    elevation_preference: Optional[str] = "media"
    scenic_preference: Optional[str] = "media"
    traffic_avoidance: Optional[str] = "media"
    loop: bool = False
    training_goal: Optional[str] = None