import logging
import random

import discord
from discord.ext import commands

from models.farm import FarmModel
from models.user import UserModel
from utils.currency import format_currency
from utils.emoji_map import EMOJI_MAP
from utils.users import require_user

logger = logging.getLogger(__name__)


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="setup", description="Start your farm")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def setup(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        if not farm:
            farm = FarmModel(discord_id=str(ctx.author.id), plot={})
            await farm.save_plot()

        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not user:
            user = UserModel(discord_id=str(ctx.author.id),
                             balance=100, inventory={},
                             created_at=discord.utils.utcnow(), stats={})
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

        random_tip = random.choice([
            "Use </inventory:1207866795147657219> to view your inventory.",
            "Use </stats:1207963367864795207> to view statistics about your farm.",
        ])

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Profile :farmer:",
            description=f"""**Balance**: {format_currency(profile.balance)}
**Joined**: {profile.created_at.strftime("%b %d, %Y")}

{random_tip}""",
            color=discord.Color.dark_gray(),
        )

        embed.set_thumbnail(url=ctx.author.avatar.url)

        return await ctx.respond({"profile": profile}, embed=embed)

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
            description="**Bonuses**\n- +500 :coin:\n\nThank you for helping us grow!",
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
        def item_type_to_name_fallback(item_type):
            name = item_type.split(":")[-1]
            return str(name).capitalize()

        def item_type_to_type(item_type):
            type = item_type.split(":")[0]
            return str(type).capitalize()

        embed = discord.Embed(
            title="Inventory",
            color=discord.Color.dark_gray(),
        )

        shop_data = getattr(self.bot, "shop_data", [])
        for item_type, item in inventory.items():
            item_name = next(
                (i.name for i in shop_data if i.type == item_type), None
            )

            if not item_name:
                logger.warning(f"Item {item_type} not found in shop data")
                item_name = item_type_to_name_fallback(item_type)

            embed.add_field(
                name=f"{EMOJI_MAP[item_type]} {item_name} – {item.amount}",
                value=f"<:RR:1207913276516859936> {item_type_to_type(item_type)}",
                inline=False
            )

        return embed


def setup(bot):
    bot.add_cog(Profile(bot))
