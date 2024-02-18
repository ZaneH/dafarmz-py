from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ChallengeOptionModel(BaseModel):
    """
    Represents an option in a challenge.
    """
    description: str = ""
    rewards: Dict[str, int | float | Any] = {}
    progress: Dict[str, int | float | Any] = {}
    goal_stats: Dict[str, int | float | Any] = {}
    accepted: bool = False


class ChallengesModel(BaseModel):
    """
    Represents the challenges that a user can complete.
    """
    last_refreshed_at: datetime = Field(default_factory=datetime.utcnow)
    options: List[ChallengeOptionModel] = []
