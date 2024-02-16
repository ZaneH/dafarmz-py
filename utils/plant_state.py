from datetime import datetime
import logging

logger = logging.getLogger(__name__)

IMAGE_YIELD_MAP = {
    "plant:apple": [
        "sapling.png",
        "apple-0.png",
        "apple-1.png",
        "apple-2.png",
    ],
    "plant:blueberry": [
        "sapling.png",
        "blueberry-0.png",
        "blueberry-1.png",
        "blueberry-2.png",
    ],
    "plant:carrot": [
        "carrot-0.png",
        "carrot-1.png",
        "carrot-2.png",
        "carrot-3.png",
    ],
    "plant:corn": [
        "corn-0.png",
        "corn-1.png",
        "corn-2.png",
        "corn-3.png",
        "corn-4.png",
    ],
    "plant:orange": [
        "sapling.png",
        "orange-0.png",
        "orange-1.png",
        "orange-2.png",
    ],
    "plant:peach": [
        "sapling.png",
        "peach-0.png",
        "peach-1.png",
        "peach-2.png",
    ],
    "plant:pear": [
        "sapling.png",
        "pear-0.png",
        "pear-1.png",
        "pear-2.png",
    ],
    "plant:pickle": [
        "pickle-0.png",
        "pickle-1.png",
        "pickle-2.png",
        "pickle-3.png",
    ],
    "plant:pumpkin": [
        "pumpkin-0.png",
        "pumpkin-1.png",
        "pumpkin-2.png",
        "pumpkin-3.png",
    ],
    "plant:strawberry": [
        "sapling.png",
        "strawberry-0.png",
        "strawberry-1.png",
        "strawberry-2.png",
    ],
    "plant:starfruit": [
        "starfruit-0.png",
        "starfruit-1.png",
        "starfruit-2.png",
        "starfruit-3.png",
    ],
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
