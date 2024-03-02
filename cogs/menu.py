import discord
from discord.ext import commands

from views.main_menu_view import MainMenuView


def create_main_menu_embed():
    embed = discord.Embed(
        title="Main Menu",
        description="""Welcome to DaFarmz!

__Command Center__:
- Help: Get a list of useful commands.
- Profile: View and customize your profile.
- Challenges: Complete for rewards.
- About: Learn about DaFarmz.

__Odyssey__:
- Farm: Manage your farms.
- Explore: Discover new lands and collect materials.
- Fish: Catch aquatic creatures and loot.
- Battle: Fight for glory and gold.

__Colony Actions__:
- Shop: Buy and sell items.
- Craft: Create new upgrades, tools, and weaponry.
- Inventory: Manage all of your items.
- Upgrade: Improve your colony and its facilities.

*Command your farm into the future.*
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
