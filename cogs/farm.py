import logging

import discord
from discord import SlashCommandGroup
from discord.ext import commands

from images.render import render_farm
from models.plots import PlotModel
from models.users import UserModel
from utils.embeds import create_farm_embed, create_scenario_embed
from utils.emoji_map import EMOJI_MAP
from utils.shop import name_to_shop_item
from utils.users import require_user
from utils.yields import harvest_yield_to_list
from views.choose_seed_view import ChooseSeedView
from views.farm_view import FarmView
from views.scenario_view import ScenarioView

logger = logging.getLogger(__name__)


class Farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    plot = SlashCommandGroup("plot", description="Manage your farm")

    async def start_farm_view(
            self, ctx: discord.context.ApplicationContext, farm: PlotModel):
        farm_view = FarmView(farm, ctx.author)
        await ctx.respond(embed=create_farm_embed(ctx.author.display_name),
                          view=farm_view,
                          files=[await render_farm(farm)])

    async def start_explore_view(
            self, ctx: discord.context.ApplicationContext, profile: UserModel):
        explore_view = ScenarioView(profile)
        await ctx.respond(
            embed=create_scenario_embed(profile),
            view=explore_view
        )

    @commands.slash_command(name="farm", description="View your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def farm(self, ctx: discord.context.ApplicationContext):
        farm = await PlotModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, farm):
            return

        await self.start_farm_view(ctx, farm)

    @plot.command(name="view", description="View your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def plot_view(self, ctx: discord.context.ApplicationContext):
        farm = await PlotModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, farm):
            return

        await self.start_farm_view(ctx, farm)

    @plot.command(name="explore", description="Look for new plots to expand your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def plot_explore(self, ctx: discord.context.ApplicationContext):
        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, user):
            return

        await self.start_explore_view(ctx, user)

    @commands.slash_command(name="harvest", description="Harvest your farm")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def harvest(self, ctx: discord.context.ApplicationContext):
        farm = await PlotModel.find_by_discord_id(ctx.author.id)
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

        formatted_yield = harvest_yield_to_list(harvest_yield)

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
        seed: discord.Option(str, "Seed to plant", required=False) # type: ignore
    ):
        # fmt: on
        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, user):
            return

        if seed:
            farm = await PlotModel.find_by_discord_id(ctx.author.id)
            item = name_to_shop_item(seed)

            if item and farm.plant(location, item):
                await farm.save_plot()
                await ctx.respond(f"You've planted a {seed} on your farm!")
                await UserModel.inc_stat(user.discord_id, f"plant.{item.key}")
            else:
                await ctx.respond("You can't plant that here!")
        else:
            async def _on_plant_callback(seed, view: ChooseSeedView):
                farm = await PlotModel.find_by_discord_id(ctx.author.id)
                if farm.plant(location, seed):
                    await farm.save_plot()
                    await view.message.edit(f"You've planted a {seed.name} {EMOJI_MAP[seed.key]} on {location}!", view=None)
                    await UserModel.inc_stat(user.discord_id, f"plant.{seed.key}")
                else:
                    await view.message.edit("You can't plant that here!", view=None)

            choose_plant_view = ChooseSeedView()
            choose_plant_view.chose_seed_callback = _on_plant_callback
            await ctx.respond("Choose something to plant on your farm", view=choose_plant_view)


def setup(bot):
    bot.add_cog(Farm(bot))
