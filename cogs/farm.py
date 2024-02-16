import io
import logging

import discord
from discord.ext import commands
from db.shop_data import ShopData

from images.merge import generate_image
from models.farm import FarmModel
from models.user import UserModel
from utils.users import require_user

logger = logging.getLogger(__name__)


class Farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="farm", description="View your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def farm(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, farm):
            return

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
        if not await require_user(ctx, farm):
            return

        harvest_yield = farm.harvest()
        await farm.save_plot()

        await UserModel.give_items(ctx.author.id, harvest_yield)
        logger.info(f"User {ctx.author.id} harvested {harvest_yield}")

        if not any(harvest_yield.values()):
            return await ctx.respond("You don't have anything to harvest!")

        await UserModel.inc_stats(ctx.author.id, {
            "harvest.count": 1,
            **{
                f"harvest.{item_key}": amount
                for item_key, amount in harvest_yield.items()
            }
        })

        return await ctx.respond("You've harvested your farm!")

    @commands.slash_command(name="plant", description="Plant a crop on your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def plant(self, ctx: discord.context.ApplicationContext, location: str, plant: str):
        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, user):
            return

        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        shop_data = ShopData.data()
        item = next((item for item in shop_data if item.key == plant), None)

        if item and farm.plant(location, item):
            await farm.save_plot()
            return await ctx.respond(f"You've planted a {plant} on your farm!")
        else:
            return await ctx.respond("You can't plant that here!")


def setup(bot):
    bot.add_cog(Farm(bot))
