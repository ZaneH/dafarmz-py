from datetime import datetime
import logging

import discord
from discord.ext import commands
from db.shop_data import ShopData

from models.shop import ShopModel
from models.user import UserModel
from utils.currency import format_currency
from utils.emoji_map import EMOJI_MAP
from utils.users import require_user
from views.sale_view import SaleView

logger = logging.getLogger(__name__)


def create_receipt(receipt_kind, buyer_discord_id, item_name, quantity, value):
    logger.info(
        f"{receipt_kind} from {buyer_discord_id}: {quantity}x {item_name}")

    receipt = discord.Embed(
        title="Jason's Shop",
        description=f"Receipt for <@{buyer_discord_id}>",
        color=discord.Color.random()
    )

    receipt.add_field(name="Item", value=item_name)
    receipt.add_field(name="Quantity", value=quantity)
    if receipt_kind == "buy":
        receipt.add_field(name="Total",
                          value=f"-{format_currency(value)}")
    else:
        receipt.add_field(name="Total",
                          value=f"+{format_currency(value)}")

    formatted_date = datetime.utcnow().strftime(
        "%b %d, %Y")
    receipt.set_footer(
        text=f"Thank you, come again!\n{formatted_date}")
    return receipt


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="shop", description="View the shop")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx: discord.context.ApplicationContext):
        shop_data = ShopData.buyable()
        if len(shop_data) == 0:
            return await ctx.respond("Shop is not ready yet. Come back later.", ephemeral=True)

        embed = discord.Embed(title="Jason's Shop",
                              color=discord.Color.blurple())
        embed.set_thumbnail(url="https://i.imgur.com/3CQRKGY.png")
        for item in shop_data:
            embed.add_field(
                name=f"{EMOJI_MAP.get(item.key, '')} {item.name}",
                value=f"{EMOJI_MAP['ui:reply']} {format_currency(item.cost)}",
                inline=False
            )

        await ctx.respond(embed=embed, ephemeral=True)

    def get_purchasables(ctx: discord.AutocompleteContext):
        type = ctx.options['type']
        shop_data = ShopData.buyable()

        plant_shop_items = [
            item.name for item in shop_data if 'plant' in item.key.lower()]
        match type:
            case 'Plants':
                return plant_shop_items

        return ['⏳ Coming soon...']

    @commands.slash_command(name="buy", description="Buy an item from the shop")
    @commands.cooldown(5, 8, commands.BucketType.user)
    async def buy(self,
    # fmt: off
                  ctx: discord.context.ApplicationContext,
                  type: discord.Option(str, choices=['Plants', 'Machines', 'Tools', 'Upgrades'], description="The type of item to buy", required=False), # type: ignore
                  name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_purchasables), description="The name of the item to buy", required=False), # type: ignore
                  amount: discord.Option(int, description="The amount of the item to buy", required=False) = 1): # type: ignore
    # fmt: on
        if not await require_user(ctx, await UserModel.find_by_discord_id(ctx.author.id)):
            return

        shop_data = ShopData.buyable()
        if len(shop_data) == 0:
            return await ctx.respond("Shop is not ready yet. Come back later.", ephemeral=True)

        # Handle the case where no options are provided
        if type is None and name is None:
            sale_view = SaleView(shop_data, "buy")

            async def _on_purchase_callback(view, item, item_name, quantity, cost):
                success = await UserModel.give_item(ctx.author.id, item, quantity, cost)
                if success:
                    receipt = create_receipt(
                        "buy",
                        ctx.author.id, item_name, quantity, cost)

                    if isinstance(view, SaleView):
                        await view.message.edit(content="Transaction completed.", view=None)

                    await ctx.respond(embed=receipt)
                else:
                    await ctx.respond("You don't have enough to buy that.", ephemeral=True)

            sale_view.on_purchase_callback = _on_purchase_callback
            await ctx.respond("## Jason's Shop", view=sale_view, ephemeral=True)
        else:
            full_item = next(
                (item for item in shop_data if item.name == name), None)
            if full_item is None:
                return await ctx.respond("Item not found.", ephemeral=True)

            value_amount = full_item.cost * amount
            success = await UserModel.give_item(ctx.author.id, full_item.key, amount, value_amount)
            if success:
                receipt = create_receipt(
                    "buy",
                    ctx.author.id, name, amount,
                    value_amount
                )

                await ctx.respond(embed=receipt)
            else:
                await ctx.respond("You don't have enough to buy that.", ephemeral=True)

    @commands.slash_command(name="sell", description="Sell an item from your inventory")
    @commands.cooldown(5, 8, commands.BucketType.user)
    async def sell(self,
    # fmt: off
                  ctx: discord.context.ApplicationContext,
                  type: discord.Option(str, choices=['Plants', 'Machines', 'Tools', 'Upgrades'], description="The type of item to buy", required=False), # type: ignore
                  name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_purchasables), description="The name of the item to buy", required=False), # type: ignore
                  amount: discord.Option(int, description="The amount of the item to sell", required=False) = 1): # type: ignore
    # fmt: on
        if not await require_user(ctx, await UserModel.find_by_discord_id(ctx.author.id)):
            return

        shop_data = ShopData.buyable()
        if len(shop_data) == 0:
            return await ctx.respond("Shop is not ready yet. Come back later.", ephemeral=True)

        if type is None and name is None:
            sale_view = SaleView(shop_data, "sell")

            async def _on_purchase_callback(view, item, item_name, quantity, cost):
                success = await UserModel.remove_item(ctx.author.id, item, quantity)
                if success:
                    receipt = create_receipt(
                        "sell",
                        ctx.author.id, item_name, quantity, cost)

                    if isinstance(view, SaleView):
                        await view.message.edit(content="Transaction completed.", view=None)

                    await ctx.respond(embed=receipt)
                else:
                    await ctx.respond("You don't have enough to do that.", ephemeral=True)

            sale_view.on_purchase_callback = _on_purchase_callback
            await ctx.respond("## Jason's Shop", view=sale_view, ephemeral=True)
        else:
            full_item = next(
                (item for item in shop_data if item.name == name), None)
            if full_item is None:
                return await ctx.respond("Item not found.", ephemeral=True)

            value_amount = full_item.resell_price * amount
            success = await UserModel.remove_item(ctx.author.id, full_item.key, amount, value_amount)
            if success:
                receipt = create_receipt(
                    "sell",
                    ctx.author.id, name, amount,
                    value_amount
                )

                await ctx.respond(embed=receipt)
            else:
                await ctx.respond("You don't have enough to do that.", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Load shop data when bot is ready.
        """
        all_items = await ShopModel.find_all()
        buyable_items = await ShopModel.find_buyable()

        ShopData.get_instance().all_shop_data = all_items
        ShopData.get_instance().buyable_data = buyable_items


def setup(bot):
    bot.add_cog(Shop(bot))
