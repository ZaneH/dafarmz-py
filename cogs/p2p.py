from datetime import datetime
import logging

import discord
from discord.ext import commands

from models.shop import ShopModel
from models.user import UserModel
from utils.currency import format_currency
from views.sale_view import SaleView

logger = logging.getLogger(__name__)


def create_transfer_receipt(receipt_kind, sender_discord_id, recipient_discord_id, amount):
    logger.info(
        f"{receipt_kind} from {sender_discord_id} to {recipient_discord_id}: {amount}"
    )

    receipt = discord.Embed(
        title="Transfer :money_with_wings:",
        description=f"Receipt for <@{sender_discord_id}>",
        color=discord.Color.random()
    )

    receipt.add_field(name="Recipient", value=f"<@{recipient_discord_id}>")
    receipt.add_field(name="Amount", value=f"-{format_currency(amount)}")

    formatted_date = datetime.utcnow().strftime(
        "%b %d, %Y")
    receipt.set_footer(
        text=f"Thank you for using DaPayments!\n{formatted_date}")
    return receipt


class P2P(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="pay", description="Pay another user")
    async def pay(self, ctx: discord.context.ApplicationContext, user: discord.User, amount: float):
        if amount <= 0:
            return await ctx.respond("Stop being stingy, you can only pay someone with an amount greater than 0.", ephemeral=True)

        # Database stores balance in cents
        amount = int(amount * 100)

        user_model = await UserModel.find_by_discord_id(ctx.author.id)
        if user_model.balance < amount:
            return await ctx.respond(f"You don't have enough money!\n**Balance**: {format_currency(user_model.balance)}", ephemeral=True)

        user_model.balance -= amount
        await user_model.save()

        recipient_model = await UserModel.find_by_discord_id(user.id)
        if recipient_model is None:
            return await ctx.respond("Recipient does not have a farm.\nAsk them to create one using `/setup` and try again.", ephemeral=True)

        recipient_model.balance += amount
        await recipient_model.save()

        await ctx.respond(embed=create_transfer_receipt("Transfer", ctx.author.id, user.id, amount))


def setup(bot):
    bot.add_cog(P2P(bot))
