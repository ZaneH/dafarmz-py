from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from db.database import get_collection
from models.pyobjectid import PyObjectId

COLLECTION_NAME = "users"


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
    discord_id: str
    created_at: datetime
    balance: int
    inventory: Dict[str, UserInventoryItem]

    @classmethod
    async def find_by_discord_id(cls, discord_id):
        collection = get_collection(COLLECTION_NAME)
        doc = await collection.find_one({
            "discord_id": str(discord_id)
        })

        return cls(**doc) if doc else None

    async def save(self):
        collection = get_collection(COLLECTION_NAME)
        await collection.replace_one({"_id": self.id}, self.model_dump(), upsert=True)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        from_attributes = True
