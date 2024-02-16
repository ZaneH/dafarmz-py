from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from db.database import Database
from models.pyobjectid import PyObjectId
from models.shop import ShopModel
from utils.plant_state import can_harvest


COLLECTION_NAME = "farms"


class BasePlotItemData(BaseModel):
    """
    Potential data for a plot item. This model is used to represent the
    data attached to each plot item in the user's farm.
    """
    yields_remaining: Optional[int] = None
    last_harvested_at: Optional[datetime] = None
    yields: Optional[Dict[str, int]] = None
    grow_time_hr: Optional[float] = None


class FarmPlotItem(BaseModel):
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


class FarmModel(BaseModel):
    """
    Represents a user's farm in the database. This model contains info about
    what is currently planted in the user's farm.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    discord_id: str
    plot: Dict[str, FarmPlotItem]

    @classmethod
    async def find_by_discord_id(cls, discord_id):
        collection = Database.get_instance().get_collection(COLLECTION_NAME)
        doc = await collection.find_one({
            "discord_id": str(discord_id)
        })

        return cls(**doc) if doc else None

    def harvest(self):
        harvest_yield = {}
        dead_plot_items = []
        for plot_id, plot_item in self.plot.items():
            if plot_item.data and plot_item.data.yields_remaining > 0:
                is_ready = can_harvest(
                    plot_item.key,
                    plot_item.data.last_harvested_at,
                    plot_item.data.grow_time_hr
                )

                if not is_ready:
                    continue

                plot_item.data.yields_remaining -= 1
                plot_item.data.last_harvested_at = datetime.utcnow()

                if plot_item.data.yields_remaining == 0:
                    dead_plot_items.append(plot_id)

                yields = getattr(plot_item.data, "yields", {})
                for k, v in yields.items():
                    if k in harvest_yield:
                        harvest_yield[k] += v
                    else:
                        harvest_yield[k] = v

        # Remove dead plot items (no yields remaining)
        for plot_item in dead_plot_items:
            del self.plot[plot_item]

        return harvest_yield

    def plant(self, location: str, item: ShopModel):
        # Check if the plot location is already taken
        if self.plot.get(location):
            return False

        yields = item.yields
        yields_remaining = item.yields_remaining
        grow_time_hr = item.grow_time_hr

        self.plot[location] = FarmPlotItem(
            key=item.key,
            data=BasePlotItemData(
                yields_remaining=yields_remaining,
                last_harvested_at=datetime.utcnow(),
                yields=yields,
                grow_time_hr=grow_time_hr
            )
        )

        return True

    async def save_plot(self):
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
