from datetime import datetime
import random
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from db.database import Database

COLLECTION_NAME = "challenges"


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

    @classmethod
    async def generate(cls, for_level: int):
        """
        Generate random challenges for a user based on their level.
        """
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        cursor = collection.find({
            "level": {"$lte": for_level}
        })

        challenges = await cursor.to_list(length=None)

        # Shuffle the challenges
        random.shuffle(challenges)

        # Limit to 3 challenges
        challenges = challenges[:3]

        return cls(
            last_refreshed_at=datetime.utcnow(),
            options=[
                ChallengeOptionModel(**challenge) for challenge in challenges
            ],
        )
