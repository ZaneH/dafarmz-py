from datetime import datetime
import logging

logger = logging.getLogger(__name__)

IMAGE_YIELD_MAP = {
    "plant:crystalline_cabbage": [
        "crystalline-cabbage-0.png",
        "crystalline-cabbage-1.png",
        "crystalline-cabbage-2.png",
        "crystalline-cabbage-3.png",
        "crystalline-cabbage-4.png",
    ],
    "plant:frost_lettuce": [
        "frost-lettuce-0.png",
        "frost-lettuce-1.png",
        "frost-lettuce-2.png",
        "frost-lettuce-3.png",
        "frost-lettuce-4.png",
        "frost-lettuce-5.png",
    ],
    "plant:polar_peppers": [
        "polar-peppers-0.png",
        "polar-peppers-1.png",
        "polar-peppers-2.png",
        "polar-peppers-3.png",
        "polar-peppers-4.png",
    ]
}


def get_stage(item: str, last_harvested: datetime, grow_time_hr: float):
    """
    Determine the stage of the plant based on the item, yields remaining, and
    last harvested date.

    :param item: The item to determine the stage for (e.g. "plant:apple")
    :param last_harvested: The date the plant was last harvested
    :return: The stage of the plant
    """
    images = IMAGE_YIELD_MAP.get(item)
    if not images:
        return 0

    if not grow_time_hr:
        logger.warning(f"Item {item} does not have a grow time")
        return 0

    # If never harvested before, return stage 0
    if not last_harvested:
        return 0

    # Handle plant stages
    time_since_last_harvest = (
        datetime.utcnow() - last_harvested).total_seconds()
    time_per_yield = grow_time_hr * 3600
    time_elapsed = time_since_last_harvest / time_per_yield
    stage = max(0, min(len(images), int(time_elapsed * len(images))) - 1)

    return stage


def can_harvest(item: str, last_harvested: datetime, grow_time_hr: float):
    """
    Determine if the plant can be harvested. Stage must be at the final stage
    to be considered harvestable.

    :param item: The item to determine the stage for (e.g. "plant:apple")
    :param last_harvested: The date the plant was last harvested
    :return: True if the plant can be harvested, False otherwise
    """
    images = IMAGE_YIELD_MAP.get(item)
    if not images:
        return False

    stage = get_stage(item, last_harvested, grow_time_hr)
    return stage is not None and stage == len(images) - 1


def get_image_for_plot_item_state(item: str, last_harvested: datetime, grow_time_hr: float):
    """
    Get the image path for the plant stage based on the item, yields remaining,
    and last harvested date.

    :param item: The item to determine the stage for (e.g. "plant:apple")
    :param last_harvested: The date the plant was last harvested
    :return: The image path for the plant stage
    """
    images = IMAGE_YIELD_MAP.get(item)
    if not images:
        raise ValueError(f"Item {item} does not have an image map")

    stage = get_stage(item, last_harvested, grow_time_hr)
    if isinstance(images, str):
        return images

    return images[stage]
