import discord
from discord.ext import commands
from models.farm import FarmModel


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = None

    @commands.slash_command(name="profile", description="View your profile information")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def farm(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        print(farm.plot["A3"].item_type)
        return await ctx.respond("Hi", ephemeral=True)


def setup(bot):
    bot.add_cog(Profile(bot))
