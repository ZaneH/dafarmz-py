import io
import discord
from discord.ext import commands
from images.merge import generate_image
from models.farm import FarmModel


class Farm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_data = None

    @commands.slash_command(name="farm", description="View your farm")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def farm(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        image = generate_image(farm.plot)
        with io.BytesIO() as image_binary:
            image.save(image_binary, "PNG")
            image_binary.seek(0)
            file = discord.File(image_binary, filename="farm.png")
            return await ctx.respond(file=file)

    @commands.slash_command(name="harvest", description="Harvest your farm")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def harvest(self, ctx: discord.context.ApplicationContext):
        farm = await FarmModel.find_by_discord_id(ctx.author.id)
        farm.harvest()
        await farm.save_plot()
        return await ctx.respond("You've harvested your farm!")


def setup(bot):
    bot.add_cog(Farm(bot))
