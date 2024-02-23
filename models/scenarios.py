from typing import Dict, Optional
from db.database import Database

from models.plots import PlotModel, PlotItem
from utils.level_calculator import xp_to_level

COLLECTION_NAME = "scenarios"


class ScenarioPlotItem(PlotItem):
    """
    Represents a single plot item in the scenario. This model contains
    info about what is currently planted in a plot space in the scenario.
    """
    growth_stage: Optional[int] = 0  # When the player arrives, what stage is the plant in?

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class ScenarioModel(PlotModel):
    """
    Represents a single scenario in the database. This model contains
    info about what is available in this scenario. Typically contains
    plants, items, and other things that are available in the scenario.
    """
    plot: Dict[str, ScenarioPlotItem] = {}

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
