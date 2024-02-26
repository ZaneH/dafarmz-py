import discord
from discord.ext import commands

from db.planets_data import PlanetsData
from models.planets import PlanetModel
from utils.embeds import create_planet_embed
from views.planets_view import PlanetsView


class Planets(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="planets", description="View information about each planet in the game.")
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def planets(self, ctx: discord.context.ApplicationContext):
        """
        /planets - View information about each planet in the game.
        """
        planets_view = PlanetsView()
        page = planets_view.pagination.get_page()
        if len(page) == 0:
            return await ctx.send("No planets found.")

        return await ctx.send(
            embed=create_planet_embed(page[0]),
            view=planets_view
        )

    @commands.Cog.listener()
    async def on_ready(self):
        PlanetsData.get_instance().all_planets = await PlanetModel.find_all()


def setup(bot):
    bot.add_cog(Planets(bot))
