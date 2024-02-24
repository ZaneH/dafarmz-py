import discord
from db.shop_data import ShopData
from models.shop_items import ShopItemModel
from utils.embeds import create_shop_embed
from utils.pagination import PaginationHelper
from views.submenu_view import SubmenuView


class ShopView(SubmenuView):
    def __init__(self, timeout=120):
        super().__init__(timeout=timeout)

        self.pagination = PaginationHelper[ShopItemModel](
            ShopData.buyable(), 8)

        self.prev_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="← Prev",
            row=2,
        )
        self.prev_button.callback = self.on_prev_button_clicked
        self.add_item(self.prev_button)

        self.next_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Next →",
            row=2,
        )
        self.next_button.callback = self.on_next_button_clicked
        self.add_item(self.next_button)

        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = not self.pagination.has_previous_page()
        self.next_button.disabled = not self.pagination.has_next_page()

    async def on_prev_button_clicked(self, interaction: discord.Interaction):
        self.pagination.previous_page()
        self.update_buttons()

        await self.update_message(interaction)

    async def on_next_button_clicked(self, interaction: discord.Interaction):
        self.pagination.next_page()
        self.update_buttons()

        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="",
            embed=create_shop_embed(self.pagination.get_page()),
            view=self,
            files=[],
            attachments=[]
        )
