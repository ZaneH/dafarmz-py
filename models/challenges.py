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
    max_active: int = 1
    options: List[ChallengeOptionModel] = []

    @classmethod
    async def generate(cls, for_level: int, amount=3):
        """
        Generate random challenges for a user based on their level.
        Can be used to fetch one or more challenges.

        :param for_level: The level of the user as int.
        :param amount: The amount of challenges to fetch.
        :return: A new instance of `ChallengesModel`.
        """
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        cursor = collection.find({
            "level": {"$lte": for_level}
        })

        challenges = await cursor.to_list(length=None)

        # Shuffle the challenges
        random.shuffle(challenges)

        # Limit to `amount` challenges
        challenges = challenges[:amount]

        return cls(
            last_refreshed_at=datetime.utcnow(),
            options=[
                ChallengeOptionModel(**challenge) for challenge in challenges
            ],
        )
