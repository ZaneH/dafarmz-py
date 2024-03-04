import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from fastapi import FastAPI
from api.fastapi import router

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
logger = logging.getLogger()  # Get the root logger

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s')
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('PIL.PngImagePlugin').setLevel(logging.WARNING)


class DaFarmz(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix={"."},
            intents=discord.Intents.default(),
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="the farm"),
        )

    async def on_connect(self):
        await self.sync_commands()

    async def on_ready(self):
        logger.info(
            f"{self.user} is ready..."
        )

        from views.challenges_view import ChallengesView
        from views.farm_view import FarmView
        from views.main_menu_view import MainMenuView
        from views.planets_view import PlanetsView
        from views.sale_view import SaleView
        from views.scenario_view import ScenarioView
        from views.select_location_view import SelectLocationView
        from views.shop_view import ShopView

        self.add_view(MainMenuView())
        self.add_view(ScenarioView())
        self.add_view(FarmView())
        self.add_view(ChallengesView())
        self.add_view(ShopView())
        self.add_view(SaleView(buy_or_sell="buy"))
        self.add_view(PlanetsView())
        self.add_view(SelectLocationView())


bot = DaFarmz()
app = FastAPI()
app.include_router(router)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.load_extension("jishaku")


async def run():
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await bot.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
