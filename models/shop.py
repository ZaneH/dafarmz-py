from typing import Dict

from bson import ObjectId
from pydantic import BaseModel, Field

from db.database import Database
from models.pyobjectid import PyObjectId
from models.yieldmodel import YieldModel

COLLECTION_NAME = "shop"


class ShopModel(BaseModel):
    """
    Represents a singular shop item from the database.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    key: str = ""  # The unique key for the item
    name: str = ""  # The display name of the item
    cost: int = 0  # The cost of the item (coins)
    grow_time_hr: float = 1  # The time it takes to grow per yield
    resell_price: int = 0  # The price to resell the item
    yields: Dict[str, YieldModel] = {}  # The yields of the item
    # The yields of the item when it dies
    death_yields: Dict[str, YieldModel] = {}
    total_yields: int = 0  # The amount of yields the item can produce
    level_required: int = 0  # The level required to see this item in the shop

    @classmethod
    async def find_all(cls):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        cursor = collection.find({})
        items = await cursor.to_list(length=None)
        items = [cls(**item) for item in items]

        return items

    @classmethod
    async def find_buyable(cls):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        cursor = collection.find({
            "cost": {"$gt": 0}
        })
        items = await cursor.to_list(length=None)
        items = [cls(**item) for item in items]

        return items

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
