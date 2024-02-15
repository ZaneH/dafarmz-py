from datetime import datetime

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
        "sapling.png",
        "carrot-0.png",
        "carrot-1.png",
        "carrot-2.png",
        "carrot-3.png",
    ],
    "plant:corn": [
        "sapling.png",
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
        "sapling.png",
        "pickle-0.png",
        "pickle-1.png",
        "pickle-2.png",
        "pickle-3.png",
    ],
    "plant:pumpkin": [
        "sapling.png",
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
    "treasure": "chest.png",
}


def get_image_for_plot_item_state(item: str, last_harvested: datetime, grow_time_hr: int):
    """
    Determine the stage of the plant based on the item, yields remaining, and
    last harvested date.

    :param item: The item to determine the stage for (e.g. "plant:apple")
    :param last_harvested: The date the plant was last harvested
    :return: The stage of the plant
    """
    images = IMAGE_YIELD_MAP.get(item)
    if not images:
        return None

    # Handle treasure chests
    if isinstance(images, str):
        return images

    # Handle plant stages
    time_since_last_harvest = (
        datetime.utcnow() - last_harvested).total_seconds()
    time_per_yield = grow_time_hr * 3600
    time_elapsed = time_since_last_harvest / time_per_yield
    stage = max(0, min(len(images), int(time_elapsed * len(images))) - 1)

    return images[stage]
