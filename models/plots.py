from datetime import datetime
import logging
import random
from typing import Any, Dict, Optional, Tuple

from bson import ObjectId
from pydantic import BaseModel, Field

from db.database import Database
from models.pyobjectid import PyObjectId
from models.shop_items import ShopItemModel
from models.yields import YieldModel
from utils.environments import Environment
from utils.plant_state import can_harvest
from utils.yields import get_yield_with_odds

logger = logging.getLogger(__name__)

COLLECTION_NAME = "farms"


class BasePlotItemData(BaseModel):
    """
    Potential data for a plot item. This model is used to represent the
    data attached to each plot item in the user's farm.
    """
    yields_remaining: Optional[int] = None  # How many yields are remaining before death
    # The last time the plot was harvested
    last_harvested_at: Optional[datetime] = None
    # Dict of items that the plot item will yield when harvested
    yields: Dict[str, YieldModel] = {}
    # The yields that the plot item will yield when it dies
    death_yields: Optional[Dict[str, YieldModel]] = {}
    # The time it takes for the plot item to grow
    grow_time_hr: Optional[float] = None

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
    environment: Environment = Environment.BARREN_WASTELANDS

    @classmethod
    def generate_random(cls):
        random_environment = random.choice(list(Environment))
        random_plot = {}
        for i in range(5):
            if random.random() > 0.5:
                random_plot[f"A{i}"] = PlotItem(
                    key="plant:apple",
                    data=BasePlotItemData(
                        yields_remaining=5,
                        last_harvested_at=datetime.utcnow(),
                        yields={
                            "plant:apple": YieldModel(amount=1)
                        },
                        grow_time_hr=2
                    )
                )

        return cls(
            discord_id=None,
            plot=random_plot,
            environment=random_environment
        )

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
                is_ready = can_harvest(
                    plot_item.key,
                    plot_item.data.last_harvested_at,
                    plot_item.data.grow_time_hr
                )

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
                last_harvested_at=datetime.utcnow(),
                yields=yields,
                death_yields=death_yields,
                grow_time_hr=grow_time_hr
            )
        )

        return True

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


class FarmModel(PlotModel):
    discord_id: Optional[str] = None

    @classmethod
    async def find_by_discord_id(cls, discord_id):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        doc = await collection.find_one({
            "discord_id": str(discord_id)
        })

        return cls(**doc) if doc else None

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }
