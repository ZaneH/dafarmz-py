from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from db.database import get_collection
from models.pyobjectid import PyObjectId


COLLECTION_NAME = "farms"


class FarmPlotItem(BaseModel):
    """
    Represents a single plot item in the user's farm. This model contains
    info about what is currently planted in a plot space.

    `item_type` is the type of item that is currently planted in the plot.
    Typically prefixed with `<type>:` where `<type>` is the type of item.
    `data` is any additional information about the plot space.
    """
    class BasePlotItemData:
        yields_remaining: int
        last_harvested_at: datetime

    item_type: str
    data: Optional[BasePlotItemData | Any] = None

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class FarmModel(BaseModel):
    """
    Represents a user's farm in the database. This model contains info about
    what is currently planted in the user's farm.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    discord_id: str
    plot: Dict[str, FarmPlotItem]

    @classmethod
    async def find_by_discord_id(cls, discord_id):
        collection = get_collection(COLLECTION_NAME)
        doc = await collection.find_one({
            "discord_id": str(discord_id)
        })

        return cls(**doc) if doc else None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        from_attributes = True
