from datetime import datetime
from typing import Dict, Optional

from db.database import Database
from models.plots import BasePlotItemData, PlotItem, PlotModel
from utils.level_calculator import xp_to_level

COLLECTION_NAME = "scenarios"


class ScenarioPlotItemData(BasePlotItemData):
    """
    Represents the data for a single plot item in the scenario. This model
    contains info about what is currently planted in a plot space in the scenario.
    """
    growth_stage: Optional[int] = 0  # When the player arrives, what stage is the plant in?


class ScenarioPlotItem(PlotItem):
    """
    Represents a single plot item in the scenario. This model contains
    info about what is currently planted in a plot space in the scenario.
    """
    data: Optional[ScenarioPlotItemData] = None

    def get_stage(self):
        """
        Returns the stage of the plant in the plot space.
        """
        if self.data.growth_stage is None:
            return super().get_stage()
        else:
            return self.data.growth_stage

    def set_to_harvested(self):
        """
        Sets the plant to harvested. Sets the growth stage to None so
        that it can regrow after harvesting.
        """
        self.data.growth_stage = None
        return super().set_to_harvested()

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
