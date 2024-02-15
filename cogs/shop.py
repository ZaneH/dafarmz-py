import discord
from discord.ext import commands
from models.shop import ShopModel
from utils.currency import format_currency


def get_purchasables(ctx: discord.AutocompleteContext):
    item_category = ctx.options['item_category']
    match item_category:
        case 'Plants':
            return ['Apple', 'Carrot', 'Blueberry', 'Pumpkin', 'Corn', 'Orange', 'Peach', 'Starfruit', 'Pickle', 'Strawberry']

    return ['⏳ Coming soon...']


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = None

    @commands.slash_command(name="shop", description="View the shop")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx: discord.context.ApplicationContext):
        if self.shop_data is None:
            return await ctx.respond("Shop is not ready yet. Come back later.", ephemeral=True)

        embed = discord.Embed(title="Shop", color=discord.Color.blurple())
        for item in self.shop_data:
            embed.add_field(
                name=item.name,
                value=f"Price: {format_currency(item.cost)}",
                inline=False
            )

        await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name="buy", description="Buy an item from the shop")
    @commands.cooldown(5, 8, commands.BucketType.user)
    # fmt: off
    async def buy(self,
                  ctx: discord.context.ApplicationContext,
                  type: discord.Option(str, choices=['Plants', 'Machines', 'Tools', 'Upgrades']), # type: ignore
                  name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_purchasables))): # type: ignore
    # fmt: on
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Load shop data when bot is ready.
        """
        self.shop_data = await ShopModel.find_all()


def setup(bot):
    bot.add_cog(Shop(bot))
