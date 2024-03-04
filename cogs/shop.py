from datetime import datetime
import logging

import discord
from discord.ext import commands
from db.shop_data import ShopData

from models.shop_items import ShopItemModel
from models.users import UserModel
from utils.currency import format_currency
from utils.embeds import create_shop_embed, create_shop_item_embed
from utils.shop import name_to_shop_item
from utils.users import require_user
from views.sale_view import SaleView
from views.shop_view import ShopView

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
                          value=f"-{format_currency(abs(value))}")
    else:
        receipt.add_field(name="Total",
                          value=f"+{format_currency(abs(value))}")

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
        shop_view = ShopView()
        embed = create_shop_embed(shop_view.pagination.get_page())
        await ctx.respond(
            embed=embed,
            view=shop_view,
        )

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
        if not await require_user(ctx, await UserModel.get_profile(ctx.author.id)):
            return

        shop_data = ShopData.buyable()
        if len(shop_data) == 0:
            return await ctx.respond("Shop is not ready yet. Come back later.", ephemeral=True)

        # Handle the case where no options are provided
        if type is None and name is None:
            sale_view = SaleView("buy")

            await ctx.respond("## Jason's Shop", view=sale_view, ephemeral=True)
        else:
            full_item = name_to_shop_item(name)
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
        if not await require_user(ctx, await UserModel.get_profile(ctx.author.id)):
            return

        shop_data = ShopData.buyable()
        if len(shop_data) == 0:
            return await ctx.respond("Shop is not ready yet. Come back later.", ephemeral=True)

        if type is None and name is None:
            sale_view = SaleView("sell")

            await ctx.respond("## Jason's Shop", view=sale_view, ephemeral=True)
        else:
            full_item = name_to_shop_item(name)
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

    def autocomplete_purchasables(ctx: discord.AutocompleteContext):
        category = ctx.options['category']
        name = ctx.options['name']
        shop_data = ShopData.buyable()

        if len(shop_data) == 0 or len(name) == 0:
            return [item.name for item in shop_data]

        prefix = ""
        match category:
            case "Plants & Seeds":
                prefix = ["seed:", "plant:"]
            case "Machines":
                prefix = ["machine:"]
            case "Tools & Weapons":
                prefix = ["tool:", "weapon:"]
            case "Clothing & Accessories":
                prefix = ["clothing:", "accessory:"]
            case _:
                prefix = ["none:"]

        matching_items = []
        for item in shop_data:
            if item.key.startswith(tuple(prefix)) \
                    and name.lower() in item.name.lower():
                matching_items.append(item.name)

        return matching_items[:25]

    @commands.slash_command(name="info", description="View information about an item in the shop")
    @commands.cooldown(3, 8, commands.BucketType.user)
    async def info(self,
    # fmt: off
    ctx: discord.context.ApplicationContext,
    category: discord.Option(str, choices=[
        'Plants & Seeds', 'Machines', 'Tools & Weapons', 'Clothing & Accessories'
    ], description="What are you looking to buy?", required=False), # type: ignore
    name: discord.Option(
        str,
        autocomplete=autocomplete_purchasables,
        description="The name of the item to buy", required=False
    )): # type: ignore
    # fmt: on
        # TODO: Put file and embed into a function within a view for /info
        item = name_to_shop_item(name)
        image_path = item.get_ripe_image_path() if item else None
        file = discord.File(
            image_path, filename=f"{image_path.split('/')[-1]}" if image_path else None
        )

        embed = create_shop_item_embed(item, file)

        await ctx.respond(
            embed=embed,
            file=file,
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Load shop data when bot is ready.
        """
        all_items = await ShopItemModel.find_all()
        buyable_items = await ShopItemModel.find_buyable()

        # Populate shop data
        ShopData.get_instance().all_shop_data = all_items
        ShopData.get_instance().buyable_data = buyable_items


def setup(bot):
    bot.add_cog(Shop(bot))
