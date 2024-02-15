from bson import ObjectId
from pydantic import BaseModel, Field
from db.database import get_collection
from models.pyobjectid import PyObjectId

COLLECTION_NAME = "shop"


class ShopModel(BaseModel):
    """
    Represents a singular shop item from the database.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    name: str
    cost: int
    time: int

    @classmethod
    async def find_all(cls):
        collection = get_collection(COLLECTION_NAME)
        cursor = collection.find({})
        items = await cursor.to_list(length=None)
        items = [cls(**item) for item in items]

        return items

    class Config:
        json_encoders = {
            ObjectId: str
        }
        from_attributes = True
