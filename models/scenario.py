from typing import Dict
from pydantic import BaseModel
from db.database import Database

from models.farm import FarmPlotItem
from utils.environments import Environment
from utils.level_calculator import xp_to_level

COLLECTION_NAME = "scenarios"


class ScenarioModel(BaseModel):
    """
    Represents a single scenario in the database. This model contains
    info about what is available in this scenario. Typically contains
    plants, items, and other things that are available in the scenario.
    """
    plot: Dict[str, FarmPlotItem] = {}
    environment: Environment

    @classmethod
    async def find_scenarios(cls, current_xp: int):
        """
        Finds all scenarios that are available to the user based on their
        current XP level.
        """
        level = xp_to_level(current_xp)
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        cursor = collection.find({
            "level_required": {"$lte": level}
        })

        list = await cursor.to_list(length=None)

        return [cls(**scenario) for scenario in list]

    def get_obstructions(self):
        """
        Returns a list of obstructions that are present in the scenario.
        Obstructions are prefixed with `obstruction:` in the key.
        """
        obstructions = []
        for item in self.plot.values():
            if item.key.startswith("obstruction:"):
                obstructions.append(item)

        return obstructions

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
