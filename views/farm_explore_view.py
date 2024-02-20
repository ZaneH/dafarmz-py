import discord
from images.render import render_farm

from models.farm import FarmModel
from utils.embeds import create_explore_embed, create_farm_embed


class FarmExploreView(discord.ui.View):
    async def on_timeout(self):
        self.clear_items()
        self.stop()
        await self.message.edit(view=None)

    def __init__(self, profile=None, timeout=120):
        super().__init__(timeout=timeout)

        self.profile = profile
        self.explore_button = None
        self.back_button = None

        self.add_stage_one_buttons()

    def add_stage_one_buttons(self):
        self.remove_item(self.explore_button)
        self.explore_button = discord.ui.Button(
            style=discord.ButtonStyle.primary, label="Explore")
        self.explore_button.callback = self.on_explore_button_clicked
        self.add_item(self.explore_button)

    def remove_stage_one_buttons(self):
        self.remove_item(self.explore_button)

    def add_back_button(self):
        self.remove_item(self.back_button)
        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary, label="Back")
        self.back_button.callback = self.on_back_button_clicked
        self.add_item(self.back_button)

    def remove_back_button(self):
        self.remove_item(self.back_button)

    async def on_explore_button_clicked(self, interaction: discord.Interaction):
        random_plot = FarmModel.generate_random()

        self.remove_stage_one_buttons()
        self.add_back_button()

        await interaction.response.edit_message(
            files=[await render_farm(random_plot)],
            embed=create_explore_embed(self.profile),
            view=self
        )

    async def on_back_button_clicked(self, interaction: discord.Interaction):
        await self.message.edit(
            embed=create_explore_embed(self.profile),
            view=self
        )

        self.remove_back_button()
        self.add_stage_one_buttons()

        await interaction.response.edit_message(files=[], view=self)
