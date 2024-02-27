import logging
import os
from typing import Dict

from PIL import Image

from models.plots import PlotItem

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


def generate_image(
    bg_file_name: str,
    plot_state: Dict[str, PlotItem],
    with_ui=True,  # TODO: Implement this by layering the UI on top
):
    """
    Generate an image of the plot.

    :param bg_file_name: The file name of the variant/biome background
    :param plot_state: The state of the farm plot
    :param with_ui: Whether to include the UI (A1, A2, B5, etc.)
    :return: The generated image
    """
    base_image = Image.open(
        f"./images/files/new/plots/planets/{bg_file_name}.png"
    ).convert("RGBA")

    # plot_state is a dict (A1, A2, B5, etc.)
    for plot_id, state in plot_state.items():
        col, row = plot_id[0], plot_id[1:]

        try:
            item_image = state.get_image()
            file_path = f"./images/files/new/crops/{item_image}"
            if not os.path.exists(file_path):
                logger.error(f"Image does not exist: {file_path}")
                file_path = f"./images/files/new/unknown.png"

            if item_image:
                base_image = place_object(
                    base_image,
                    file_path,
                    ord(col) - 64,
                    int(row)
                )
        except Exception as e:
            logger.error(f"Error placing object for {plot_id}: {e}")

    return base_image


def apply_cursor(image, plot_id: str):
    """
    Apply a cursor to the image.

    :param image: The image to apply the cursor to.
    :param plot_id: Position of the cursor.
    :return: The image with the cursor applied.
    """
    col, row = plot_id[0], plot_id[1:]

    cursor_image = Image.open(
        f"./images/files/new/ui/plot-cursor-box.png").convert("RGBA")
    x = (ord(col) - 64) * GRID_SIZE + PLOT_OFFSET_X - 3
    y = int(row) * GRID_SIZE + PLOT_OFFSET_Y - 3
    image.paste(cursor_image, (x, y), cursor_image)
    return image
