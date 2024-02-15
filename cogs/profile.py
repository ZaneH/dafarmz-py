import discord
from discord.ext import commands
from models.farm import FarmModel
from models.user import UserModel
from utils.currency import format_currency
from utils.users import require_user


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = None

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
                             created_at=discord.utils.utcnow())
            await user.save()

        return await ctx.respond("You're all set! Use `/help` to get started.")

    @commands.slash_command(name="profile", description="View your profile information")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def profile(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.find_by_discord_id(ctx.author.id)
        if await require_user(ctx, profile):
            embed = discord.Embed(
                title=f":farmer: {ctx.author.display_name}'s Profile",
                description=f"**Balance**: {format_currency(profile.balance)} coins",
                color=discord.Color.dark_gray(),
            )
            embed.set_thumbnail(url=ctx.author.avatar.url)

            return await ctx.respond({"profile": profile}, embed=embed)

    @commands.slash_command(name="inventory", description="View your inventory")
    @commands.cooldown(1, 6, commands.BucketType.user)
    async def inventory(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.find_by_discord_id(ctx.author.id)
        if await require_user(ctx, profile):
            return await ctx.respond({"inventory": profile.inventory}, ephemeral=True)

    @commands.slash_command(name="vote", description="Vote for the bot for rewards")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def vote(self, ctx: discord.context.ApplicationContext):
        embed = discord.Embed(
            title=":tractor: Vote for DaFarmz :ear_of_rice:",
            description="**Bonuses**\n- +500 coins\n- 1x random seed\n\nVote on the following platforms:",
            fields=[
                discord.EmbedField(
                    name="Top.gg",
                    value="[Vote here](https://top.gg/bot/1141161773983088640/vote)"
                ),
            ],
            color=discord.Color.green()
        )

        return await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Profile(bot))
