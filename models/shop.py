from typing import Dict
from bson import ObjectId
from pydantic import BaseModel, Field
from db.database import Database
from models.pyobjectid import PyObjectId

COLLECTION_NAME = "shop"


class ShopModel(BaseModel):
    """
    Represents a singular shop item from the database.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    name: str = ""
    cost: int = 0
    key: str = "Plants"
    grow_time_hr: float = 1
    resell_price: int = 0
    yields: Dict[str, int] = {}
    yields_remaining: int = 0

    @classmethod
    async def find_all(cls):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        cursor = collection.find({})
        items = await cursor.to_list(length=None)
        items = [cls(**item) for item in items]

        return items

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
