import discord
from typing import Generic, TypeVar

from models.users import RobotModel
from utils.embeds import create_robot_embed

T = TypeVar('T')


class PaginationHelper(Generic[T]):
    def __init__(self, data=None, per_page=1):
        self.data: list[T] = data or []
        self.per_page = per_page
        self.page = 0

    def get_page(self):
        start = self.page * self.per_page
        end = start + self.per_page
        return self.data[start:end]

    def next_page(self):
        self.page += 1
        return self.get_page()

    def previous_page(self):
        self.page -= 1
        return self.get_page()

    def has_next_page(self):
        return (self.page + 1) * self.per_page < len(self.data)

    def has_previous_page(self):
        return self.page > 0


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
