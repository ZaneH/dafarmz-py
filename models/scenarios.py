from typing import Dict, Optional
import logging

from pydantic import Field
from db.database import Database
from models.plots import BasePlotItemData, PlotItem, PlotModel
from utils.level_calculator import xp_to_level

logger = logging.getLogger(__name__)

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
    data: ScenarioPlotItemData = Field(default_factory=ScenarioPlotItemData)

    def get_stage(self):
        """
        Returns the stage of the plant in the plot space.
        """
        if self.data.growth_stage is None:
            return super().get_stage()
        else:
            return self.data.growth_stage

    def update_harvested_at(self):
        """
        Sets the plant to harvested image.
        """
        if self.has_harvested_image:
            self.data.growth_stage = len(self.lifecycle_images) - 1
        else:
            self.data.growth_stage = 0

        return super().update_harvested_at()

    def get_image(self):
        """
        Returns the image for the current stage of the plant.
        """
        stage = self.get_stage()
        try:
            return self.lifecycle_images[stage]
        except:
            return super().get_image()

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
