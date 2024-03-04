import logging

import discord
from discord.ext import commands

from models.plots import PlotModel
from models.users import UserModel
from utils.embeds import create_profile_embed, inventory_to_embed
from utils.emoji_map import EMOJI_MAP
from utils.shop import key_to_shop_item
from utils.users import require_user
from views.profile_view import ProfileView
from views.submenu_view import SubmenuView
from views.vote_view import VoteView

logger = logging.getLogger(__name__)


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="register", description="Get started with EdenRPG!")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def register(self, ctx: discord.context.ApplicationContext):
        farm = await PlotModel.find_by_discord_id(ctx.author.id)
        if not farm:
            farm = PlotModel(discord_id=str(ctx.author.id), plot={})
            await farm.save_plot()

        user = await UserModel.get_profile(ctx.author.id)
        if not user:
            user = UserModel(discord_id=str(ctx.author.id),
                             balance=100, inventory={},
                             created_at=discord.utils.utcnow(), stats={
                                 "xp": 0, "harvest": {"count": 0}},
                             challenges={},
                             config={})
            await user.save()

        return await ctx.respond("You're all set! Use `/help` to get started.")

    @commands.slash_command(name="profile", description="View your profile information")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def profile(self, ctx: discord.context.ApplicationContext):
        """
        /profile - View the user's profile.
        """
        profile = await UserModel.get_profile(ctx.author.id)
        if not await require_user(ctx, profile):
            return

        embed = create_profile_embed(profile, ctx.author)
        view = ProfileView()

        return await ctx.respond(embed=embed, view=view)

    @commands.slash_command(name="inventory", description="View your inventory")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def inventory(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.get_profile(ctx.author.id)
        back_view = SubmenuView()
        if await require_user(ctx, profile):
            return await ctx.respond(
                embed=inventory_to_embed(profile.inventory),
                view=back_view
            )

    @commands.slash_command(name="vote", description="Vote for the bot to earn rewards")
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def vote(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.get_profile(ctx.author.id)
        if not await require_user(ctx, profile):
            return

        embed = discord.Embed(
            title="Vote for DaFarmz :ear_of_rice:",
            description=f"""**Bonuses**
- +500 {EMOJI_MAP["item:coin"]} for each vote

Thank you for helping us grow!""",
            color=discord.Color.embed_background()
        )

        vote_view = VoteView()
        return await ctx.respond(
            embed=embed,
            view=vote_view
        )

    @commands.slash_command(name="stats", description="View your farming stats")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def stats(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.get_profile(ctx.author.id)
        if not await require_user(ctx, profile):
            return

        return await ctx.respond(profile.stats)


def setup(bot):
    bot.add_cog(Profile(bot))
