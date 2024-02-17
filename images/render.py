import io

import discord

from images.merge import generate_image
from models.farm import FarmModel


async def render_farm(farm: FarmModel):
    image = generate_image(farm.plot)
    with io.BytesIO() as image_binary:
        image.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(image_binary, filename="farm.png")
        return file
