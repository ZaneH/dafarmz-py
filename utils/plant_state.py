from datetime import datetime
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class LifecycleInfo:
    """
    Lifecycle information for a plant
    """

    def __init__(self, lifecycle=None, has_harvested=True):
        if lifecycle is None:
            lifecycle = []
        self.lifecycle = lifecycle
        self.has_harvested = has_harvested


IMAGE_YIELD_MAP = {
    "plant:crystalline_cabbage": LifecycleInfo(
        lifecycle=[
            "crystalline-cabbage-0.png",
            "crystalline-cabbage-1.png",
            "crystalline-cabbage-2.png",
            "crystalline-cabbage-3.png",
            "crystalline-cabbage-4.png",
        ],
        has_harvested=False
    ),
    "plant:polar_peppers": LifecycleInfo(
        lifecycle=[
            "polar-peppers-0.png",
            "polar-peppers-1.png",
            "polar-peppers-2.png",
            "polar-peppers-3.png",
            "polar-peppers-4.png",
        ],
        has_harvested=True
    ),
    "plant:iceburg_lettuce": LifecycleInfo(
        lifecycle=[
            "iceburg-lettuce-0.png",
            "iceburg-lettuce-1.png",
            "iceburg-lettuce-2.png",
            "iceburg-lettuce-3.png",
            "iceburg-lettuce-4.png",
            "iceburg-lettuce-5.png",
        ],
        has_harvested=True
    ),
}
