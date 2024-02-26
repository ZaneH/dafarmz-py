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


LIFECYCLE_MAP = {
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
            "polar-peppers-5.png",
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
    "plant:apple_bush": LifecycleInfo(
        lifecycle=[
            "apple-bush-0.png",
            "apple-bush-1.png",
            "apple-bush-2.png",
            "apple-bush-3.png",
            "apple-bush-4.png",
        ],
        has_harvested=True
    ),
    "plant:dusty_rye": LifecycleInfo(
        lifecycle=[
            "dusty-rye-0.png",
            "dusty-rye-1.png",
            "dusty-rye-2.png",
            "dusty-rye-3.png",
            "dusty-rye-4.png",
            "dusty-rye-5.png",
        ],
        has_harvested=True
    )
}


def get_ripe_image(plant_key: str) -> str:
    """
    Returns the ripe image for the plant. If `has_harvested` is True, then
    the ripe image is the second to last image in the lifecycle. Otherwise, the
    ripe image is the last image in the lifecycle.
    """
    lifecycle_info = LIFECYCLE_MAP.get(plant_key)
    if lifecycle_info is None:
        logger.error(f"Could not find lifecycle info for plant: {plant_key}")
        return ""

    lifecycle = lifecycle_info.lifecycle
    if lifecycle_info.has_harvested:
        return lifecycle[-2]
    else:
        return lifecycle[-1]


def build_crop_image_path(image_path: str) -> str:
    return f"./images/files/new/crops/{image_path}"
