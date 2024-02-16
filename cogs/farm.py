import io
import logging

import discord
from discord.ext import commands
from db.shop_data import ShopData

from images.merge import generate_image
from models.farm import FarmModel
from models.user import UserModel
from utils.emoji_map import EMOJI_MAP
from utils.users import require_user
from views.choose_plant_view import ChoosePlantView

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

        (harvest_yield, xp_earned) = farm.harvest()
        await farm.save_plot()

        await UserModel.give_items(ctx.author.id, harvest_yield, 0, {
            "xp": xp_earned,
            "harvest.xp": xp_earned,
            "harvest.count": 1,
            **{
                f"harvest.{item_key}": amount
                for item_key, amount in harvest_yield.items()
            }
        })

        logger.info(f"User {ctx.author.id} harvested {harvest_yield}")

        formatted_yield = ""
        for item, amount in harvest_yield.items():
            formatted_yield += f"{EMOJI_MAP[item]} {amount}x\n"

        if not any(harvest_yield.values()):
            return await ctx.respond("You don't have anything to harvest!")

        return await ctx.respond(f"""You've harvested your farm and earned +**{xp_earned} XP**!

{formatted_yield}""")

    @commands.slash_command(name="plant", description="Plant a crop on your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def plant(self,
        # fmt: off
                    ctx: discord.context.ApplicationContext,
                    location: discord.Option(str, "The location to plant the crop (e.g. A1)", required=True), # type: ignore
                    plant: discord.Option(str, "What to plant", required=False)): # type: ignore
        # fmt: on
        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, user):
            return

        if plant:
            farm = await FarmModel.find_by_discord_id(ctx.author.id)
            shop_data = ShopData.data()
            item = next(
                (item for item in shop_data if item.key == plant), None)

            if item and farm.plant(location, item):
                await farm.save_plot()
                return await ctx.respond(f"You've planted a {plant} on your farm!")
            else:
                return await ctx.respond("You can't plant that here!")
        else:
            async def _on_plant_callback(plant, view: ChoosePlantView):
                farm = await FarmModel.find_by_discord_id(ctx.author.id)
                if farm.plant(location, plant):
                    await farm.save_plot()
                    return await view.message.edit(f"You've planted a {plant.name} {EMOJI_MAP[plant.key]} on {location}!", view=None)
                else:
                    return await view.message.edit("You can't plant that here!", view=None)

            choose_plant_view = ChoosePlantView()
            choose_plant_view.chose_plant_callback = _on_plant_callback
            await ctx.respond("Choose something to plant on your farm", view=choose_plant_view)


def setup(bot):
    bot.add_cog(Farm(bot))
