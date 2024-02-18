import discord
from discord.ui.item import Item

from db.shop_data import ShopData


class ChooseSeedView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

        self.chose_seed_callback = None

        self.shop_data = ShopData.buyable()
        seeds = [item for item in self.shop_data if "seed:" in item.key]

        self.seed_select = discord.ui.Select(
            placeholder="Choose a plant",
            options=[
                discord.SelectOption(
                    label=plant.name,
                    value=plant.key
                ) for plant in seeds
            ],
        )

        self.seed_select.callback = self.on_select_seed_callback

        self.add_item(self.seed_select)

    async def on_select_seed_callback(self, interaction: discord.Interaction):
        self.selected_plant = next(
            plant for plant in self.shop_data if plant.key == interaction.data["values"][0])

        if self.chose_seed_callback:
            await self.chose_seed_callback(self.selected_plant, self)

        await interaction.response.defer()

    async def on_timeout(self):
        await self.message.edit("Selection timed out.", view=None)
