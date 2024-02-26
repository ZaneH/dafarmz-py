from db.planets_data import PlanetsData
from utils.embeds import create_planet_embed
from views.pagination_view import PaginationView
import discord


class PlanetsView(PaginationView):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout, data=PlanetsData.all())

        self.update_message_callback = self.on_update_message

        self.update_buttons()

    async def on_update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="",
            embed=create_planet_embed(self.pagination.get_page()),
            view=self,
            files=[],
            attachments=[]
        )
