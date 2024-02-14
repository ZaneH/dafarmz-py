from bson import ObjectId
from pydantic import BaseModel, Field
from db.database import get_collection
from models.pyobjectid import PyObjectId


class ShopModel:
    COLLECTION_NAME = "shop"

    @classmethod
    async def find_all(cls):
        collection = get_collection(cls.COLLECTION_NAME)
        cursor = collection.find({})
        items = await cursor.to_list(length=None)
        items = [ShopItem(**item) for item in items]

        return items
    
class ShopItem(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    name: str
    cost: int
    time: int

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        from_attributes = True