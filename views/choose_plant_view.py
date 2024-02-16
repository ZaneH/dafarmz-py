import discord
from discord.ui.item import Item

from db.shop_data import ShopData


class ChoosePlantView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

        self.chose_plant_callback = None

        self.shop_data = ShopData.data()
        plants = [item for item in self.shop_data if "plant:" in item.key]

        self.plant_select = discord.ui.Select(
            placeholder="Choose a plant",
            options=[
                discord.SelectOption(
                    label=plant.name,
                    value=plant.key
                ) for plant in plants
            ],
        )

        self.plant_select.callback = self.on_select_plant_callback

        self.add_item(self.plant_select)

    async def on_select_plant_callback(self, interaction: discord.Interaction):
        self.selected_plant = next(
            plant for plant in self.shop_data if plant.key == interaction.data["values"][0])

        if self.chose_plant_callback:
            await self.chose_plant_callback(self.selected_plant, self)

        await interaction.response.defer()

    async def on_timeout(self):
        await self.message.edit("Selection timed out.", view=None)
