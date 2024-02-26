import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo import ReturnDocument

from db.database import Database
from models.challenges import ChallengesModel
from models.pyobjectid import PyObjectId
from models.yields import YieldModel
from utils.level_calculator import xp_to_level

logger = logging.getLogger(__name__)

COLLECTION_NAME = "users"


class ConfigModel(BaseModel):
    last_planet_id: ObjectId = ObjectId("60f3b3e3e4e508f3e3e3e3e3")
    """The ID of the last planet the user visited. Default is Verdantia."""
    last_biome: int = 0
    """The index of the last biome the user visited. Default is 0."""

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class UserInventoryItem(BaseModel):
    """
    Represents an arbitrary `amount` of items in the user's inventory.
    Any additional information could be added to `data` but nothing is
    making use of it yet.
    """
    amount: int
    data: Optional[Any] = None


class UserModel(BaseModel):
    """
    Represents a user in the database. This model is used to interact with
    the database and should only be used to interact with the database. This model
    is not used to interact with the user in the bot.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    discord_id: str = ""
    """Discord ID of the user as str."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    """The date and time the user was created as datetime."""
    balance: int = 0
    """The user's balance as int."""
    inventory: Dict[str, UserInventoryItem] = {}
    """The user's inventory as a dictionary of `UserInventoryItem`."""
    stats: Dict[str, int | float | Any] = {}
    """The user's stats as a dictionary of int or float."""
    challenges: ChallengesModel = Field(
        default_factory=ChallengesModel)
    """The user's challenges as a `ChallengesModel`."""
    config: ConfigModel = Field(default_factory=ConfigModel)
    """The user's configuration as a `ConfigModel`."""
    unlocked_planets: List[ObjectId] = []

    @classmethod
    async def find_by_discord_id(cls, discord_id):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        doc = await collection.find_one({
            "discord_id": str(discord_id)
        })

        return cls(**doc) if doc else None

    @classmethod
    async def give_items(
        cls,
        discord_id,
        items: Dict[str, YieldModel],
        cost=0,
        stats: Dict[str, int | float | Any] = {}
    ):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        inc_inventory = {}
        for item, yields in items.items():
            inc_inventory[f"inventory.{item}.amount"] = yields.amount

        inc_stats = {}
        for stat, yield_ in stats.items():
            if isinstance(yield_, YieldModel):
                # inc_stats = {f"stats.{stat}.{key}": value for key,
                #              value in amount.model_dump().items()}
                inc_stats = {}
                for key, value in yield_.model_dump().items():
                    if key == "amount":
                        inc_stats[f"stats.{stat}.{key}"] = value
            else:
                inc_stats[f"stats.{stat}"] = yield_

        result = await collection.find_one_and_update(
            {
                "discord_id": str(discord_id),
                "balance": {"$gte": cost}
            },
            {
                "$inc": {
                    "balance": -cost,
                    **inc_inventory,
                    **inc_stats
                },
            },
            return_document=ReturnDocument.AFTER
        )

        return cls(**result) if result else None

    @classmethod
    async def give_item(cls, discord_id, item, amount, cost=0):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        result = await collection.update_one(
            {
                "discord_id": str(discord_id),
                "balance": {"$gte": cost}
            },
            {
                "$inc": {
                    f"inventory.{item}.amount": amount,
                    "balance": -cost
                },
            },
        )

        return result.modified_count > 0

    @classmethod
    async def remove_item(cls, discord_id, item, amount, compensation=0):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        result = await collection.update_one(
            {
                "discord_id": str(discord_id),
                f"inventory.{item}.amount": {"$gte": amount}
            },
            {
                "$inc": {
                    f"inventory.{item}.amount": -amount,
                    "balance": compensation
                },
            },
        )

        return result.modified_count > 0

    @classmethod
    async def inc_stat(cls, discord_id, stat, amount=1):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        result = await collection.update_one(
            {
                "discord_id": str(discord_id),
            },
            {
                "$inc": {
                    f"stats.{stat}": amount
                },
            },
        )

        return result.modified_count > 0

    @classmethod
    async def inc_stats(cls, discord_id, stats: Dict[str, int | float | Any]):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        result = await collection.update_one(
            {
                "discord_id": str(discord_id),
            },
            {
                "$inc": {
                    f"stats.{stat}": amount
                    for stat, amount in stats.items()
                },
            },
        )

        return result.modified_count > 0

    @classmethod
    async def accept_challenge(cls, discord_id, challenge_index):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        result = await collection.find_one_and_update(
            {
                "discord_id": str(discord_id),
                f"challenges.options.{challenge_index}": {"$exists": True},
            },
            {
                "$set": {
                    f"challenges.options.{challenge_index}.accepted": True
                },
            },
            return_document=ReturnDocument.AFTER
        )

        return cls(**result) if result else None

    @classmethod
    async def refresh_challenges(
            cls,
            discord_id: str,
            current_xp: int,
            last_refreshed_at: datetime,
            max_active=1
    ):
        current_time = datetime.utcnow()

        if (current_time - last_refreshed_at).total_seconds() < 86400:
            raise ValueError("You can only refresh challenges once per day.")

        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        challenges = await ChallengesModel.generate(xp_to_level(current_xp) + 1)
        challenges.max_active = max_active

        result = await collection.find_one_and_update(
            {
                "discord_id": str(discord_id),
            },
            {
                "$set": {
                    "challenges": challenges.model_dump()
                },
            },
            return_document=ReturnDocument.AFTER
        )

        return cls(**result) if result else None

    @classmethod
    async def increment_challenge_progress(cls, discord_id, action, item, increment=1):
        """
        Increment the progress of a challenge for a user.

        :param discord_id: The discord ID of the user as int.
        :param action: The action to increment as str. (e.g. "harvest", "plant", "buy")
        :param item: The item key to increment as str.
        :param increment: The amount to increment as int.
        :return: A new instance of `UserModel` if the user was found, else None.
        """
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        user = await collection.find_one({"discord_id": str(discord_id)})

        if not user:
            return None  # User not found

        for index, challenge in enumerate(user["challenges"]["options"]):
            if challenge.get("accepted", False) and action in challenge["goal_stats"]:
                # Check if the item matches what's required in the goal_stats
                if item in challenge["goal_stats"][action]:
                    # Increment progress
                    progress_path = f"challenges.options.{index}.progress.{action}.{item}"
                    await collection.update_one(
                        {"discord_id": str(discord_id)},
                        {"$inc": {progress_path: increment}}
                    )

        # Return the updated user document
        updated_user = await collection.find_one({"discord_id": str(discord_id)})
        return cls(**updated_user) if updated_user else None

    async def claim_challenge_rewards(self, challenge_index: int) -> Optional["UserModel"]:
        """
        Use .give_items() to claim the rewards for a challenge.
        Remove the challenge from the user's challenges.

        :param challenge_index: The index of the challenge to claim as int.
        :return: A new instance of `UserModel` if the user was found, else None.
        """
        if not self.challenges or challenge_index >= len(self.challenges.options):
            logger.warning(
                f"User {self.discord_id} tried to claim a challenge that doesn't exist: {challenge_index}"
            )
            raise ValueError("Invalid challenge index. Something went wrong.")

        # Convert rewards to YieldModel
        rewards = self.challenges.options[challenge_index].rewards
        rewards_to_give = {key: YieldModel(
            key=key, amount=amount
        ) for key, amount in rewards.items()}

        # XP is a stat, not an item. We need to handle it separately.
        xp_earned = 0
        for key, reward in rewards_to_give.items():
            if key == "item:xp":
                xp_earned = reward.amount
                break

        # Coins are also handled separately.
        coins_earned = 0
        for key, reward in rewards_to_give.items():
            if key == "item:coin":
                coins_earned = reward.amount
                break

        # Filter out the XP and coins from the rewards to give.
        rewards_to_give = {
            key: reward for key, reward in rewards_to_give.items()
            if key not in ["item:xp", "item:coin"]
        }

        new_user = await UserModel.give_items(
            self.discord_id,
            rewards_to_give,
            coins_earned,
            stats={
                # Increment the user's XP
                "xp": xp_earned,
                "challenge.xp": xp_earned,
                "challenge.count": 1,
                **{
                    f"challenge.{item_key}": amount
                    for item_key, amount in rewards.items()
                }
            }
        )

        if new_user:
            new_user.challenges = self.challenges
            new_user.challenges.options.pop(challenge_index)
            new_challenge = await ChallengesModel.generate(
                xp_to_level(new_user.stats.get("xp", 0)) + 1, amount=1
            )
            new_user.challenges.options.append(new_challenge.options[0])
            new_challenge.max_active = self.challenges.max_active

            await new_user.save()
        else:
            logger.warning(
                f"User {self.discord_id} tried to claim challenge rewards but the user wasn't returned."
            )
            raise ValueError(
                "There was an issue claiming the challenge rewards.")

        logger.debug(
            f"User {self.discord_id} claimed challenge rewards: {rewards}")

        return new_user

    async def save(self):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        await collection.replace_one({"_id": self.id}, self.model_dump(), upsert=True)

    @property
    def current_level(self):
        return xp_to_level(self.stats.get("xp", 0))

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
