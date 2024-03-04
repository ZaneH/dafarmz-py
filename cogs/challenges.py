import discord
from discord.ext import commands
from models.users import UserModel
from utils.embeds import create_embed_for_challenges
from utils.users import require_user
from views.challenges_view import ChallengesView


class Challenges(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="challenges", description="View your daily challenges")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def challenges(self, ctx: discord.context.ApplicationContext):
        """
        /challenges - View the user's challenges.
        """
        profile = await UserModel.get_profile(ctx.author.id)
        if not await require_user(ctx, profile):
            return

        challenges_view = ChallengesView(profile)
        challenges_embed = create_embed_for_challenges(
            ctx.author.display_name, profile.challenges)
        return await ctx.respond("", view=challenges_view, embed=challenges_embed)


def setup(bot):
    bot.add_cog(Challenges(bot))
