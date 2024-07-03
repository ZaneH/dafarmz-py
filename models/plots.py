import logging
import random
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from bson import ObjectId
from pydantic import BaseModel, Field

from db.database import Database
from models.pyobjectid import PyObjectId
from models.shop_items import ShopItemModel
from models.yields import YieldModel
from utils.environments import Environment
from utils.plant_state import LIFECYCLE_MAP
from utils.yields import get_yield_with_odds

logger = logging.getLogger(__name__)

COLLECTION_NAME = "farms"


class BasePlotItemData(BaseModel):
    """
    Potential data for a plot item. This model is used to represent the
    data attached to each plot item in the user's farm.
    """
    yields_remaining: Optional[int] = None
    """How many yields are remaining before death"""
    last_harvested_at: Optional[datetime] = None
    """The last time the plot was harvested"""
    planted_at: Optional[datetime] = None
    """When the plot item was planted"""
    yields: Dict[str, YieldModel] = {}
    """Dict of items that the plot item will yield when harvested"""
    death_yields: Optional[Dict[str, YieldModel]] = {}
    """The yields that the plot item will yield when it dies"""
    grow_time_hr: Optional[float] = None
    """The time it takes for the plot item to grow"""

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class PlotItem(BaseModel):
    """
    Represents a single plot item in the user's farm. This model contains
    info about what is currently planted in a plot space.

    `key` is the identifier for what is currently planted in the plot.
    Typically prefixed with `<type>:` where `<type>` is the type of item.
    `data` is any additional information about the plot space.
    """
    key: str
    data: Optional[BasePlotItemData] = None

    @property
    def lifecycle_images(self):
        return LIFECYCLE_MAP.get(self.key, {}).lifecycle

    @property
    def has_harvested_image(self):
        return LIFECYCLE_MAP.get(self.key, {}).has_harvested

    def can_harvest_again(self):
        """
        Determine if the plant is ready to be harvested since the last
        time it was harvested.

        :return: True if the plant is ready to be harvested, False otherwise
        """
        if not self.data.last_harvested_at:
            return False

        time_since_last_harvest = (
            datetime.utcnow() - self.data.last_harvested_at).total_seconds()
        time_per_yield = self.data.grow_time_hr * 3600
        time_elapsed = time_since_last_harvest / time_per_yield

        return time_elapsed >= 1

    def can_harvest(self):
        """
        Determine if the plant can be harvested. Stage must be at the final stage
        to be considered harvestable.

        :return: True if the plant can be harvested, False otherwise
        """
        if self.data.last_harvested_at:
            return self.can_harvest_again()

        if not self.lifecycle_images:
            # Sanity check
            return False

        # Get # of images in the lifecycle
        # If the plant has a harvested image, the "ready" stage
        # is the second to last image in the lifecycle
        stage = min(self.get_stage(), len(self.lifecycle_images) - 1)
        ready_stage = min(stage, len(self.lifecycle_images) - 1)

        if self.has_harvested_image:
            stage -= 1
            ready_stage -= 1

        return stage == ready_stage

    def update_harvested_at(self):
        self.data.last_harvested_at = datetime.utcnow()

    def get_stage(self):
        """
        Determine the stage of the plant based on the item, yields remaining, and
        last harvested date.

        :return: The stage of the plant
        """
        if not self.lifecycle_images:
            return 0

        if self.data.grow_time_hr <= 0:
            logger.warning(f"Item {self.key} does not have a valid grow time")
            return 0

        # If last_harvested_at is set, the plant has been harvested before
        # If not, calculate the stage based on the planted_at date
        if self.data.last_harvested_at:
            time_since_last_harvest = (
                datetime.utcnow() - self.data.last_harvested_at).total_seconds()
        elif self.data.planted_at:
            time_since_last_harvest = (
                datetime.utcnow() - self.data.planted_at).total_seconds()
        else:
            return 0

        time_per_yield_s = self.data.grow_time_hr * 3600
        time_elapsed_s = time_since_last_harvest / time_per_yield_s

        # BUG: There's a bug here where the stage is not being calculated correctly
        print(f"Time elapsed for {self.key}: {time_elapsed_s}")

        return int(time_elapsed_s)

    def get_image(self):
        """
        Get the image path for the plant stage based on the item, yields remaining,
        and last harvested date.

        :param item: The item to determine the stage for (e.g. "plant:apple")
        :param last_harvested: The date the plant was last harvested
        :return: The image path for the plant stage
        """
        stage = self.get_stage()
        try:
            if self.key.startswith("plant:"):
                image_info = LIFECYCLE_MAP.get(self.key, None)

                if not image_info:
                    raise ValueError(
                        f"Item {self.key} does not have an image map")

                if isinstance(image_info, str):
                    return image_info

                stage = min(stage, len(self.lifecycle_images) - 1)

                if self.has_harvested_image:
                    stage = min(stage, len(self.lifecycle_images) - 2)

                return self.lifecycle_images[stage]
            elif self.key.startswith("obstruction:"):
                # Example: obstruction:rock -> obstruction-rock.png
                return f"obstruction-{self.key.split(':')[1]}.png"
        except:
            logger.warning(
                f"Couldn't get_image for {self.key} at stage {stage}")

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class PlotModel(BaseModel):
    """
    Represents a user's farm in the database. This model contains info about
    what is currently planted in the user's farm.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    plot: Dict[str, PlotItem]

    planet_id: Optional[PyObjectId] = None
    """The planet ID that this scenario is on. If None, it is randomized."""
    biome_index: int = 0
    """The index of the biome that this scenario is on."""
    variant_index: Optional[int] = None
    """The index of the variant to use for the biome. If None, it is randomized."""

    def remove_plant(self, location: str):
        if self.plot.get(location):
            del self.plot[location]

    def harvest(self) -> Tuple[Dict[str, YieldModel], int]:
        """
        Harvests the user's farm. This method will remove any dead plot items
        and return the yields and xp earned from the harvest.

        :return: A tuple containing the yields and xp earned from the harvest.
        """
        harvest_yield: Dict[str, YieldModel] = {}
        dead_plot_items = []
        xp_earned = 0

        for plot_id, plot_item in self.plot.items():
            if plot_item.data:
                is_ready = plot_item.can_harvest()

                if is_ready:
                    for yield_item in plot_item.data.yields.values():
                        xp_earned += yield_item.xp

                    plot_item.data.yields_remaining -= 1
                    plot_item.data.last_harvested_at = datetime.utcnow()

                    yields: Dict[str, YieldModel] | Any = getattr(
                        plot_item.data, "yields", {})
                    for k, v in yields.items():
                        if k in harvest_yield:
                            harvest_yield[k].amount += get_yield_with_odds(v)
                        else:
                            amount = get_yield_with_odds(v)
                            if amount > 0:
                                harvest_yield[k] = YieldModel(amount=amount)

                # Mark plot item as dead if no yields remaining
                if plot_item.data.yields_remaining <= 0:
                    dead_plot_items.append(plot_id)

        # Remove dead plot items (no yields remaining)
        for plot_item in dead_plot_items:
            # Check for death_yields and add them to the harvest_yield
            if self.plot[plot_item].data.death_yields:
                for k, v in self.plot[plot_item].data.death_yields.items():
                    # Key has already been added, just increment the amount
                    if k in harvest_yield:
                        harvest_yield[k].amount += get_yield_with_odds(v)
                    else:
                        amount = get_yield_with_odds(v)
                        if amount > 0:
                            harvest_yield[k] = YieldModel(amount=amount)

            # Remove the plot item from the plot
            self.remove_plant(plot_item)

        return (harvest_yield, xp_earned)

    def plant(self, location: str, item: ShopItemModel):
        # Check if the plot location is already taken
        if self.plot.get(location):
            return False

        # Confirm this is a seed
        if not item.key.startswith("seed:"):
            return False

        yields = item.yields
        death_yields = item.death_yields
        yields_remaining = item.total_yields
        grow_time_hr = item.grow_time_hr

        self.plot[location] = PlotItem(
            # Replace the seed type with 'plant:' after planting
            key=item.key.replace("seed:", "plant:"),
            data=BasePlotItemData(
                yields_remaining=yields_remaining,
                planted_at=datetime.utcnow(),
                last_harvested_at=None,
                yields=yields,
                death_yields=death_yields,
                grow_time_hr=grow_time_hr
            )
        )

        return True

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }


class FarmModel(PlotModel):
    discord_id: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.variant_index = 0

    @classmethod
    async def find_by_discord_id(cls, discord_id):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        doc = await collection.find_one({
            "discord_id": str(discord_id)
        })

        return cls(**doc) if doc else None

    async def save_plot(self):
        if (self.discord_id is None):
            logger.warning(
                "Attempted to save plot without a discord_id. This is likely a bug."
            )

            return

        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        await collection.update_one(
            {"_id": self.id},
            {"$set": {"plot": {k: v.model_dump() for k, v in self.plot.items()}}},
            upsert=True
        )

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
