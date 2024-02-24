import logging
import random

import discord
from discord.ext import commands
from db.shop_data import ShopData

from models.plots import PlotModel
from models.users import UserModel
from utils.currency import format_currency
from utils.embeds import create_profile_embed
from utils.emoji_map import EMOJI_MAP
from utils.level_calculator import xp_to_level, level_to_xp, next_level_xp
from utils.progress_bar import construct_xp_progress_bar
from utils.shop import key_to_shop_item
from utils.users import require_user

logger = logging.getLogger(__name__)


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="setup", description="Start your farm")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def setup(self, ctx: discord.context.ApplicationContext):
        farm = await PlotModel.find_by_discord_id(ctx.author.id)
        if not farm:
            farm = PlotModel(discord_id=str(ctx.author.id), plot={})
            await farm.save_plot()

        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not user:
            user = UserModel(discord_id=str(ctx.author.id),
                             balance=100, inventory={},
                             created_at=discord.utils.utcnow(), stats={
                                 "xp": 0, "harvest": {"count": 0}},
                             challenges={})
            await user.save()

        return await ctx.respond("You're all set! Use `/help` to get started.")

    @commands.slash_command(name="profile", description="View your profile information")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def profile(self, ctx: discord.context.ApplicationContext):
        """
        /profile - View the user's profile.
        """
        profile = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, profile):
            return

        embed = create_profile_embed(profile, ctx.author)

        return await ctx.respond(embed=embed)

    @commands.slash_command(name="inventory", description="View your inventory")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def inventory(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.find_by_discord_id(ctx.author.id)
        if await require_user(ctx, profile):
            return await ctx.respond(
                embed=self.inventory_to_embed(profile.inventory),
            )

    @commands.slash_command(name="vote", description="Vote for the bot to earn rewards")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def vote(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, profile):
            return

        embed = discord.Embed(
            title="Vote for DaFarmz :ear_of_rice:",
            description=f"""**Bonuses**
- +500 {EMOJI_MAP["item:coin"]} for each vote

Thank you for helping us grow!""",
            fields=[
                discord.EmbedField(
                    name="Top.gg",
                    value="[Vote here](https://top.gg/bot/1141161773983088640/vote)"
                ),
            ],
            color=discord.Color.embed_background()
        )

        return await ctx.respond(embed=embed)

    @commands.slash_command(name="stats", description="View your farming stats")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def stats(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.find_by_discord_id(ctx.author.id)
        if not await require_user(ctx, profile):
            return

        return await ctx.respond(profile.stats)

    def inventory_to_embed(self, inventory):
        def item_type_to_name_fallback(item_key):
            name = item_key.split(":")[-1]
            return str(name).capitalize()

        def item_key_to_type(item_key):
            type = item_key.split(":")[0]
            return str(type).capitalize()

        embed = discord.Embed(
            title="Inventory",
            color=discord.Color.dark_gray(),
        )

        for item_key, item in inventory.items():
            try:
                full_item = key_to_shop_item(item_key)
                item_name = full_item.name if full_item else None

                if not item_name:
                    logger.warning(f"Item {item_key} not found in shop data")
                    item_name = item_type_to_name_fallback(item_key)

                embed.add_field(
                    name=f"{EMOJI_MAP[item_key]} {item_name} – {item.amount}",
                    value=f"{EMOJI_MAP['ui:reply']} {item_key_to_type(item_key)}",
                    inline=False
                )
            except Exception as e:
                logger.error(
                    f"Error adding item {item_key} to inventory embed: {e}")

        return embed


def setup(bot):
    bot.add_cog(Profile(bot))
