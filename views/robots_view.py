import discord

from models.users import RobotModel
from utils.embeds import create_robot_embed
from utils.pagination import PaginationHelper


class RobotsView(discord.ui.View):
    async def on_timeout(self):
        await self.message.edit(view=None)

    def __init__(self, robots: list[RobotModel]):
        super().__init__(timeout=120)

        self.robots = robots
        self.pagination = PaginationHelper[RobotModel](robots)

        self.previous_button = discord.ui.Button(
            style=discord.ButtonStyle.primary, label="← Previous")
        self.previous_button.callback = self.on_prev_button_clicked
        self.next_button = discord.ui.Button(
            style=discord.ButtonStyle.primary, label="Next →")
        self.next_button.callback = self.on_next_button_clicked

        self.update_buttons()

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    def update_buttons(self):
        self.previous_button.disabled = not self.pagination.has_previous_page()
        self.next_button.disabled = not self.pagination.has_next_page()

    async def on_next_button_clicked(self, interaction: discord.Interaction):
        embed = create_robot_embed(self.pagination.next_page()[0])
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_prev_button_clicked(self, interaction: discord.Interaction):
        embed = create_robot_embed(self.pagination.previous_page()[0])
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
