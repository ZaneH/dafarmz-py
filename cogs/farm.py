import io
import logging

import discord
from discord.ext import commands

from images.merge import generate_image
from models.farm import FarmModel
from models.user import UserModel

logger = logging.getLogger(__name__)


class Farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = None

    @commands.slash_command(name="farm", description="View your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def farm(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        image = generate_image(farm.plot)
        with io.BytesIO() as image_binary:
            image.save(image_binary, "PNG")
            image_binary.seek(0)
            file = discord.File(image_binary, filename="farm.png")
            return await ctx.respond(file=file)

    @commands.slash_command(name="harvest", description="Harvest your farm")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def harvest(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        harvest_yield = farm.harvest()
        await farm.save_plot()

        await UserModel.give_items(ctx.author.id, harvest_yield)
        logger.info(f"User {ctx.author.id} harvested {harvest_yield}")

        if not any(harvest_yield.values()):
            return await ctx.respond("You don't have anything to harvest!")

        await UserModel.inc_stats(ctx.author.id, {
            "harvest.count": 1,
            **{
                f"harvest.{item_type}": amount
                for item_type, amount in harvest_yield.items()
            }
        })

        return await ctx.respond("You've harvested your farm!")


def setup(bot):
    bot.add_cog(Farm(bot))
