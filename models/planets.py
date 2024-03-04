from typing import List
from bson import ObjectId
from pydantic import BaseModel, Field

from db.database import Database
from models.pyobjectid import PyObjectId

COLLECTION_NAME = "planets"


def build_biome_image_path(image_name: str) -> str:
    return f"./images/files/new/plots/planets/{image_name}.png"


class PlanetBiomeModel(BaseModel):
    """
    The model for an environment on a planet.
    """
    name: str = ""
    """The name of the environment."""
    description: str = ""
    """The description of the environment."""
    backgrounds: List[str] = []
    """The backgrounds of the environment. File names."""

    @property
    def preview_background(self):
        if len(self.backgrounds) > 0:
            return build_biome_image_path(self.backgrounds[0])
        return None

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class PlanetModel(BaseModel):
    """
    The model for a planet in the game.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    """The ID of the planet."""
    name: str = ""
    """The name of the planet."""
    description: str = ""
    """The description of the planet."""

    biomes: List[PlanetBiomeModel] = []
    """The environments on this planet. In order of progression."""

    @classmethod
    async def find_all(cls):
        """
        Find all planets in the database.
        """
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        cursor = collection.find({})

        planets = await cursor.to_list(length=None)
        return [cls(**planet) for planet in planets]

    @property
    def preview_background(self):
        if len(self.biomes) > 0:
            if len(self.biomes[0].backgrounds) > 0:
                return build_biome_image_path(self.biomes[0].backgrounds[0])
        return None

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
