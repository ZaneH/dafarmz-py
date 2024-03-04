import discord

from models.users import UserModel
from views.stats_view import StatsView
from views.submenu_view import SubmenuView


class ProfileView(SubmenuView):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout, back_button_row=1)

        self.stats_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Stats",
            row=0,
        )
        self.stats_button.callback = self.on_stats_button_clicked
        self.add_item(self.stats_button)

    async def on_stats_button_clicked(self, interaction: discord.Interaction):
        from utils.embeds import create_farm_stats_embed
        profile = await UserModel.get_profile(interaction.user.id)
        stats_view = StatsView()

        await interaction.response.edit_message(
            embed=create_farm_stats_embed(profile),
            view=stats_view
        )
