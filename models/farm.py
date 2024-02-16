from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from db.database import Database
from models.pyobjectid import PyObjectId
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

    `type` is the type of item that is currently planted in the plot.
    Typically prefixed with `<type>:` where `<type>` is the type of item.
    `data` is any additional information about the plot space.
    """

    type: str
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
                    plot_item.type,
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
