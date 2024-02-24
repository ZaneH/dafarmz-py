import discord

from models.users import UserModel
from utils.embeds import create_robot_embed
from utils.users import require_user
from views.robots_view import RobotsView


class Robots(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="robots", description="List all the robots")
    async def robots(self, ctx: discord.context.ApplicationContext):
        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, user):
            return

        robots = user.robots
        view = RobotsView(robots)
        embed = create_robot_embed(robots[0])
        await ctx.send("Here are your robots:", view=view, embed=embed)


def setup(bot):
    bot.add_cog(Robots(bot))
