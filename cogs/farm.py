import io
import logging

import discord
from discord.ext import commands
from db.shop_data import ShopData

from images.render import render_farm
from models.farm import FarmModel
from models.user import UserModel
from utils.emoji_map import EMOJI_MAP
from utils.users import require_user
from views.choose_plant_view import ChoosePlantView
from views.farm_view import FarmView

logger = logging.getLogger(__name__)


class Farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_farm_embed(self, ctx: discord.context.ApplicationContext, farm: FarmModel):
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Farm",
            color=discord.Color.embed_background()
        )

        embed.set_image(url="attachment://farm.png")
        return embed

    async def start_farm_view(
            self, ctx: discord.context.ApplicationContext, farm: FarmModel):
        farm_view = FarmView(farm, ctx.author)
        await ctx.respond(embed=self.create_farm_embed(ctx, farm),
                          view=farm_view,
                          files=[await render_farm(farm)])

    @commands.slash_command(name="farm", description="View your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def farm(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, farm):
            return

        await self.start_farm_view(ctx, farm)

    @commands.slash_command(name="plot", description="View your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def farm(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, farm):
            return

        await self.start_farm_view(ctx, farm)

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
                await ctx.respond(f"You've planted a {plant} on your farm!")
                await UserModel.inc_stat(user.discord_id, f"plant.{item.key}")
            else:
                await ctx.respond("You can't plant that here!")
        else:
            async def _on_plant_callback(plant, view: ChoosePlantView):
                farm = await FarmModel.find_by_discord_id(ctx.author.id)
                if farm.plant(location, plant):
                    await farm.save_plot()
                    await view.message.edit(f"You've planted a {plant.name} {EMOJI_MAP[plant.key]} on {location}!", view=None)
                    await UserModel.inc_stat(user.discord_id, f"plant.{plant.key}")
                else:
                    await view.message.edit("You can't plant that here!", view=None)

            choose_plant_view = ChoosePlantView()
            choose_plant_view.chose_plant_callback = _on_plant_callback
            await ctx.respond("Choose something to plant on your farm", view=choose_plant_view)


def setup(bot):
    bot.add_cog(Farm(bot))
