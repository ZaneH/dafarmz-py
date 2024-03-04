from db.planets_data import PlanetsData
from models.planets import build_biome_image_path
from utils.embeds import create_planet_embed
from views.pagination_view import PaginationView
import discord


class PlanetsView(PaginationView):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout, data=PlanetsData.get_planets())

        self.update_message_callback = self.on_update_message

        self.update_buttons()

    async def on_update_message(self, interaction: discord.Interaction):
        planet_bg = self.pagination.get_page()[0].preview_background
        await interaction.response.edit_message(
            content="",
            embed=create_planet_embed(
                self.pagination.get_page(), discord.File(planet_bg)
            ),
            view=self,
            files=[],
            attachments=[]
        )

    def create_embed_and_file(self):
        page = self.pagination.get_page()
        if len(page) == 0:
            return None

        first_bg = page[0].preview_background
        file = discord.File(first_bg)

        embed = create_planet_embed(
            page[0],
            file
        )

        return (embed, file)
