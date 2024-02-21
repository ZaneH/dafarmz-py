import logging

from PIL import Image
from utils.environments import Environment

from utils.plant_state import get_image_for_plot_item_state

GRID_SIZE = 72
PLOT_OFFSET_X = 15
PLOT_OFFSET_Y = 21

logger = logging.getLogger(__name__)


def place_object(base, object_image, grid_x, grid_y):
    object = Image.open(object_image).convert("RGBA")
    w = object.width
    h = object.height
    x = grid_x * GRID_SIZE + PLOT_OFFSET_X - w // 2
    y = grid_y * GRID_SIZE + PLOT_OFFSET_Y - h // 2

    additional_offset = {x: GRID_SIZE // 2, y: GRID_SIZE // 2}
    if h > GRID_SIZE:
        additional_offset[y] -= h // 4

    base.paste(object, (
        int(x + additional_offset[x]),
        int(y + additional_offset[y])
    ), object)

    return base


def generate_image(environment: Environment, plot_state):
    """
    Generate an image of the farm based on the environment and plot state.

    :param environment: The environment of the farm (e.g. basic_fertile_soil)
    :param plot_state: The state of the farm plot
    :return: The generated image
    """
    base_image = Image.open(
        f"./images/files/new/plots/plot-{environment.value}-ui.png"
    ).convert("RGBA")

    # plot_state is a dict (A1, A2, B5, etc.)
    for plot_id, state in plot_state.items():
        col, row = plot_id[0], plot_id[1:]

        last_harvested_at = None
        grow_time_hr = None
        if state.data:
            last_harvested_at = state.data.last_harvested_at
            grow_time_hr = state.data.grow_time_hr

        try:
            item_image = get_image_for_plot_item_state(
                state.key,
                last_harvested_at,
                grow_time_hr
            )

            if item_image:
                base_image = place_object(
                    base_image,
                    f"./images/files/new/crops/{item_image}",
                    ord(col) - 64,
                    int(row)
                )
        except Exception as e:
            logger.error(f"Error placing object for {plot_id}: {e}")

    return base_image
