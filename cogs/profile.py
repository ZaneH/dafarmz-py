import discord
from discord.ext import commands
from models.farm import FarmModel
from models.user import UserModel
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
            await farm.save()

        user = await UserModel.find_by_discord_id(ctx.author.id)
        if not user:
            user = UserModel(discord_id=str(ctx.author.id),
                             balance=100, inventory={},
                             created_at=discord.utils.utcnow())
            await user.save()

        return await ctx.respond("You're all good to go! Use `/help` to get started.", ephemeral=True)

    @commands.slash_command(name="profile", description="View your profile information")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def profile(self, ctx: discord.context.ApplicationContext):
        profile = await UserModel.find_by_discord_id(ctx.author.id)
        if await require_user(ctx, profile):
            return await ctx.respond({"profile": profile}, ephemeral=True)


def setup(bot):
    bot.add_cog(Profile(bot))
