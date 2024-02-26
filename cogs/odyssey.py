import discord
from discord.ext import commands

from db.planets_data import PlanetsData
from models.planets import PlanetModel
from utils.embeds import create_planet_embed
from views.planets_view import PlanetsView


class Odyssey(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _odyssey(self, ctx: discord.context.ApplicationContext):
        planets_view = PlanetsView()
        (embed, file) = planets_view.create_embed_and_file()
        await ctx.respond(view=planets_view, embed=embed, file=file)

    @commands.slash_command(name="odyssey", description="View information about each planet in the game.")
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def odyssey(self, ctx: discord.context.ApplicationContext):
        """
        /odyssey - View information about each planet in the game.
        """
        await self._odyssey(ctx)

    @commands.slash_command(name="planets", description="View information about each planet in the game.")
    @commands.cooldown(3, 5, commands.BucketType.user)
    async def planets(self, ctx: discord.context.ApplicationContext):
        """
        /planets - View information about each planet in the game.
        """
        await self._odyssey(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        PlanetsData.get_instance().all_planets = await PlanetModel.find_all()


def setup(bot):
    bot.add_cog(Odyssey(bot))
