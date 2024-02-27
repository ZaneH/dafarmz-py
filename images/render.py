import io
import random
from typing import Dict, Optional

import discord
from db.planets_data import PlanetsData

from images.merge import generate_image
from images.merge import apply_cursor
from models.plots import PlotModel, PlotItem


async def render_farm(farm: PlotModel):
    """
    Render a farm image. Uses the first variant for farms.

    :param farm: The farm to render.
    :return: The rendered farm image.
    """
    planet_id = farm.planet_id
    biome_index = farm.biome_index
    variant_index = farm.variant_index
    biome = PlanetsData.get_biome(planet_id, biome_index)
    bg_file_name = biome.backgrounds[variant_index]
    image = generate_image(bg_file_name, farm.plot, with_ui=True)
    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(image_binary, filename="farm.png")
        return file


async def render_scenario(
    plot: Dict[str, PlotItem],
    highlight_plot_id: Optional[str] = None,
    planet_id: Optional[str] = None,
    biome_index: Optional[int] = None,
    variant_index: Optional[int] = None,
):
    """
    Render a scenario image.

    :param environment: The environment of the scenario.
    :param plot: The plot state of the scenario.
    :param plot_id: The ID of the plot to apply the cursor to.
    :return: The rendered scenario image.
    """
    biome = PlanetsData.get_biome(planet_id, biome_index)

    if variant_index is None:
        variant_index = random.randint(0, len(biome.backgrounds) - 1)

    bg_file_name = biome.backgrounds[variant_index]
    image = generate_image(bg_file_name, plot, with_ui=False)
    if highlight_plot_id:
        image = apply_cursor(image, highlight_plot_id)

    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(image_binary, filename="scenario.png")
        return file
