import discord
from discord.ext import commands
from .views.buy_view import BuyView
from models.shop import ShopModel
from utils.currency import format_currency


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = []

    @commands.slash_command(name="shop", description="View the shop")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx: discord.context.ApplicationContext):
        if len(self.shop_data) == 0:
            return await ctx.respond("Shop is not ready yet. Come back later.", ephemeral=True)

        embed = discord.Embed(title="Shop", color=discord.Color.blurple())
        for item in self.shop_data:
            embed.add_field(
                name=item.name,
                value=f"Price: {format_currency(item.cost)}",
                inline=False
            )

        await ctx.respond(embed=embed, ephemeral=True)

    def get_purchasables(ctx: discord.AutocompleteContext):
        type = ctx.options['type']
        shop_data = ctx.cog.shop_data

        plants = [item.name for item in shop_data if item.type == 'plant']
        match type:
            case 'Plants':
                return plants

        return ['⏳ Coming soon...']

    @commands.slash_command(name="buy", description="Buy an item from the shop")
    @commands.cooldown(5, 8, commands.BucketType.user)
    # fmt: off
    async def buy(self,
                  ctx: discord.context.ApplicationContext,
                  type: discord.Option(str, choices=['Plants', 'Machines', 'Tools', 'Upgrades'], description="The type of item to buy", required=False), # type: ignore
                  name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_purchasables), description="The name of the item to buy", required=False)): # type: ignore
    # fmt: on
        if type is None and name is None:
            await ctx.respond("## Shop", view=BuyView(self.shop_data), ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Load shop data when bot is ready.
        """
        self.shop_data = await ShopModel.find_all()


def setup(bot):
    bot.add_cog(Shop(bot))
