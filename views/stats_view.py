import discord
from models.users import UserModel

from views.submenu_view import SubmenuView


class StatsView(SubmenuView):
    def __init__(self, timeout=None, selected_stats="farm"):
        super().__init__(timeout=timeout)

        self.selected_stats = selected_stats

        self.farm_stats_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id="farm_stats",
            label="Farm",
            row=1,
        )
        self.farm_stats_button.callback = self.on_farm_stats_button_clicked
        self.add_item(self.farm_stats_button)

        self.explore_stats_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id="explore_stats",
            label="Explore",
            row=1,
        )
        self.explore_stats_button.callback = self.on_explore_stats_button_clicked
        self.add_item(self.explore_stats_button)

        self.update_buttons()

    def update_buttons(self):
        self.farm_stats_button.style = discord.ButtonStyle.secondary if self.selected_stats == "farm" else discord.ButtonStyle.blurple
        self.farm_stats_button.disabled = True if self.selected_stats == "farm" else False

        self.explore_stats_button.style = discord.ButtonStyle.secondary if self.selected_stats == "explore" else discord.ButtonStyle.blurple
        self.explore_stats_button.disabled = True if self.selected_stats == "explore" else False

    async def on_farm_stats_button_clicked(self, interaction: discord.Interaction):
        from utils.embeds import create_farm_stats_embed
        self.selected_stats = "farm"
        self.update_buttons()

        profile = await UserModel.find_by_discord_id(interaction.user.id)
        embed = create_farm_stats_embed(profile)
        await interaction.response.edit_message(view=self, embed=embed)

    async def on_explore_stats_button_clicked(self, interaction: discord.Interaction):
        from utils.embeds import create_explore_stats_embed
        self.selected_stats = "explore"
        self.update_buttons()

        profile = await UserModel.find_by_discord_id(interaction.user.id)
        embed = create_explore_stats_embed(profile)
        await interaction.response.edit_message(view=self, embed=embed)
