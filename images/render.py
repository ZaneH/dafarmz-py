import io
from typing import Dict, Optional

import discord

from images.merge import generate_image
from images.merge import apply_cursor
from models.plots import PlotModel, PlotItem
from utils.environments import Environment


async def render_farm(farm: PlotModel):
    """
    Render a farm image.

    :param farm: The farm to render.
    :return: The rendered farm image.
    """
    image = generate_image(farm.environment, farm.plot)
    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(image_binary, filename="farm.png")
        return file


async def render_scenario(
    environment: Environment,
    plot: Dict[str, PlotItem],
    plot_id: Optional[str] = None
):
    """
    Render a scenario image.

    :param environment: The environment of the scenario.
    :param plot: The plot state of the scenario.
    :param plot_id: The ID of the plot to apply the cursor to.
    :return: The rendered scenario image.
    """
    image = generate_image(environment, plot)
    if plot_id:
        image = apply_cursor(image, plot_id)

    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(image_binary, filename="scenario.png")
        return file
