import discord
from models.planets import PlanetModel

from utils.pagination import PaginationHelper
from views.submenu_view import SubmenuView


class PaginationView(SubmenuView):
    def __init__(self, timeout=None, data=[], per_page=1):
        super().__init__(timeout=timeout)

        self.page_data = data
        self.pagination = PaginationHelper[PlanetModel](
            self.page_data, per_page)
        self.update_message_callback = None

        self.prev_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id="prev",
            label="← Prev",
            row=2,
        )
        self.prev_button.callback = self.on_prev_button_clicked
        self.add_item(self.prev_button)

        self.next_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id="next",
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
        if self.update_message_callback:
            await self.update_message_callback(interaction)
