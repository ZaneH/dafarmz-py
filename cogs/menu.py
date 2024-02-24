import discord
from discord.ext import commands

from views.main_menu_view import MainMenuView


def create_main_menu_embed():
    embed = discord.Embed(
        title="Main Menu",
        description="""Welcome to DaFarmz! Your future farming adventure begins here.

__Main Menu__:
- Plant: Grow futuristic crops.
- Harvest: Collect your yield.
- Explore: Discover new biomes.

__Dashboard__:
- Profile: View stats and inventory.
- Quests: Complete for rewards.

__Community__:
- Vote: Earn rewards by supporting us.

__Commands__:
- /help: Get assistance.
- /about: Learn about DaFarmz.

Adventure awaits in every seed and horizon. Command your farm into the future.
""",
        color=discord.Color.blurple()
    )

    return embed


class Menu(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="menu", description="View the main menu")
    async def menu(self, ctx: discord.context.ApplicationContext):
        menu_view = MainMenuView()
        await ctx.respond(
            embed=create_main_menu_embed(),
            view=menu_view
        )


def setup(bot):
    bot.add_cog(Menu(bot))
