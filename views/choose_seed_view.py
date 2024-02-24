import discord
from discord.ui.item import Item

from db.shop_data import ShopData
from utils.shop import key_to_shop_item


class ChooseSeedView(discord.ui.View):
    async def on_timeout(self):
        await self.message.edit("Selection timed out.", view=None)

    def __init__(self):
        super().__init__(timeout=None)

        self.chose_seed_callback = None

        self.shop_data = ShopData.buyable()
        seeds = [item for item in self.shop_data if "seed:" in item.key]

        self.seed_select = discord.ui.Select(
            placeholder="Choose a plant",
            custom_id="seed_select",
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
        item_id = interaction.data["values"][0]
        self.selected_plant = key_to_shop_item(item_id)

        if self.chose_seed_callback:
            await self.chose_seed_callback(self.selected_plant, self)

        await interaction.response.defer()
