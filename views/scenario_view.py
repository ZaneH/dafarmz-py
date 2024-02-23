import logging
import random

import discord

from images.render import render_scenario
from models.scenario import ScenarioModel
from models.user import UserModel
from utils.embeds import create_scenario_embed

logger = logging.getLogger(__name__)


class ScenarioView(discord.ui.View):
    async def on_timeout(self):
        self.clear_items()
        self.stop()
        await self.message.edit(view=None)

    def __init__(self, profile: UserModel | None = None, timeout=120):
        super().__init__(timeout=timeout)

        self.selected_scenario = None
        self.profile = profile
        self.explore_button = None  # Go exploring
        self.select_button = None  # Select scenario
        self.next_button = None  # Next scenario
        self.back_button = None  # Back
        self.interaction_helper = None

        self.add_stage_one_buttons()

    def add_stage_one_buttons(self):
        """
        Buttons for finding a scenario.
        """
        self.remove_item(self.explore_button)
        self.explore_button = discord.ui.Button(
            style=discord.ButtonStyle.primary, label="Explore")
        self.explore_button.callback = self.on_explore_button_clicked
        self.add_item(self.explore_button)

    def add_stage_two_buttons(self):
        """
        Buttons for interacting with the selected scenario.
        """
        self.remove_item(self.explore_button)
        self.select_button = discord.ui.Button(
            style=discord.ButtonStyle.primary, label="Select")
        self.select_button.callback = self.on_select_button_clicked
        self.add_item(self.select_button)
        self.next_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary, label="Next")
        self.next_button.callback = self.on_explore_button_clicked
        self.add_item(self.next_button)

    def remove_stage_one_buttons(self):
        self.remove_item(self.explore_button)

    def remove_stage_two_buttons(self):
        self.remove_item(self.select_button)
        self.remove_item(self.next_button)

    def remove_scenario_buttons(self):
        if self.interaction_helper:
            self.interaction_helper.remove_buttons(self)

    def add_back_button(self):
        self.remove_item(self.back_button)
        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary, label="Back")
        self.back_button.callback = self.on_back_button_clicked
        self.add_item(self.back_button)

    def remove_back_button(self):
        self.remove_item(self.back_button)

    async def on_explore_button_clicked(self, interaction: discord.Interaction):
        self.remove_stage_two_buttons()
        self.remove_back_button()
        self.remove_scenario_buttons()

        current_xp = self.profile.stats.get("xp", 0)
        scenarios = await ScenarioModel.find_scenarios(current_xp)

        self.selected_scenario = random.choice(scenarios)
        environment = self.selected_scenario.environment
        plot = self.selected_scenario.plot

        self.remove_stage_one_buttons()
        self.add_back_button()

        self.add_stage_two_buttons()

        await interaction.response.edit_message(
            files=[await render_scenario(environment, plot)],
            embed=create_scenario_embed(self.profile),
            view=self
        )

    async def on_select_button_clicked(self, interaction: discord.Interaction):
        """
        The scenario has been selected and the user wants to interact with it.
        Present the main scenario controls.
        """
        self.remove_stage_two_buttons()
        self.remove_back_button()

        self.interaction_helper = ScenarioInteractionHelper()
        self.interaction_helper.setup_buttons()
        self.interaction_helper.add_buttons(self)
        self.interaction_helper.on_cursor_change_callback = self.on_cursor_change
        self.interaction_helper.on_exit_callback = self.on_exit_button_clicked
        self.interaction_helper.on_next_callback = self.on_explore_button_clicked
        self.interaction_helper.on_interact_callback = self.on_interact_button_clicked

        environment = self.selected_scenario.environment
        plot = self.selected_scenario.plot
        await interaction.response.edit_message(
            content="",
            files=[await render_scenario(environment, plot, self.interaction_helper.cursor_position)],
            embed=create_scenario_embed(self.profile),
            view=self
        )

    async def on_cursor_change(self, interaction: discord.Interaction):
        environment = self.selected_scenario.environment
        plot = self.selected_scenario.plot
        await interaction.response.edit_message(
            files=[await render_scenario(environment, plot, self.interaction_helper.cursor_position)],
            embed=create_scenario_embed(self.profile),
            view=self
        )

    async def on_interact_button_clicked(self, interaction: discord.Interaction):
        plot_item = self.get_plot_item()
        plot_name = self.interaction_helper.cursor_position

        if plot_item and plot_item.data.yields:
            return await interaction.response.edit_message(
                content=f"You interacted with {plot_item.key}.",
                embed=create_scenario_embed(self.profile),
                view=self
            )

        return await interaction.response.edit_message(
            content=f"You can't interact with {plot_name}.",
            embed=create_scenario_embed(self.profile),
            view=self
        )

    def get_plot_item(self):
        if not self.interaction_helper:
            return None

        cursor_position = self.interaction_helper.cursor_position
        plot = self.selected_scenario.plot
        return plot.get(cursor_position)

    async def on_exit_button_clicked(self, interaction: discord.Interaction):
        self.add_stage_one_buttons()
        self.remove_scenario_buttons()

        await interaction.response.edit_message(
            content="You left the scenario.",
            embed=create_scenario_embed(self.profile),
            files=[],
            view=self
        )

    async def on_back_button_clicked(self, interaction: discord.Interaction):
        self.remove_back_button()
        self.remove_stage_two_buttons()
        self.add_stage_one_buttons()

        await interaction.response.edit_message(files=[], view=self)


class ScenarioInteractionHelper:
    """
    Helper class for handling scenario interactions.
    """
    LETTERS = ["A", "B", "C", "D", "E"]
    NUMBERS = ["1", "2", "3", "4", "5"]

    def __init__(self) -> None:
        self.up_left = None
        self.left = None
        self.down_left = None
        self.up = None
        self.interact = None
        self.down = None
        self.up_right = None
        self.right = None
        self.down_right = None
        self.exit_button = None
        self.eat_button = None
        self.next_button = None

        self.cursor_row = 2
        self.cursor_column = 2

        self.on_cursor_change_callback = None
        self.on_interact_callback = None
        self.on_exit_callback = None
        self.on_eat_callback = None
        self.on_next_callback = None

    def setup_buttons(self):
        self.up_left = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="↖️", row=0)
        self.up_left.custom_id = "up_left"
        self.up_left.callback = self.on_move_button_clicked
        self.left = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="⬅️", row=1)
        self.left.custom_id = "left"
        self.left.callback = self.on_move_button_clicked
        self.down_left = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="↙️", row=2)
        self.down_left.custom_id = "down_left"
        self.down_left.callback = self.on_move_button_clicked
        self.up = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="⬆️", row=0)
        self.up.custom_id = "up"
        self.up.callback = self.on_move_button_clicked
        self.interact = discord.ui.Button(
            style=discord.ButtonStyle.secondary, emoji="✋", row=1)
        self.interact.callback = self.on_interact_button_clicked
        self.down = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="⬇️", row=2)
        self.down.custom_id = "down"
        self.down.callback = self.on_move_button_clicked
        self.up_right = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="↗️", row=0)
        self.up_right.custom_id = "up_right"
        self.up_right.callback = self.on_move_button_clicked
        self.right = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="➡️", row=1)
        self.right.custom_id = "right"
        self.right.callback = self.on_move_button_clicked
        self.down_right = discord.ui.Button(
            style=discord.ButtonStyle.primary, emoji="↘️", row=2)
        self.down_right.custom_id = "down_right"
        self.down_right.callback = self.on_move_button_clicked

        self.exit_button = discord.ui.Button(
            style=discord.ButtonStyle.danger, label="Exit", row=0)
        self.exit_button.callback = self.on_exit_button_clicked
        self.eat_button = discord.ui.Button(
            style=discord.ButtonStyle.green, label="Eat", row=1)
        self.eat_button.callback = self.on_eat_button_clicked
        self.next_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary, label="Next", row=2)
        self.next_button.callback = self.on_next_button_clicked

    async def on_exit_button_clicked(self, interaction: discord.Interaction):
        if self.on_exit_callback:
            await self.on_exit_callback(interaction)

    async def on_eat_button_clicked(self, interaction: discord.Interaction):
        if self.on_eat_callback:
            await self.on_eat_callback(interaction)

    async def on_next_button_clicked(self, interaction: discord.Interaction):
        if self.on_next_callback:
            await self.on_next_callback(interaction)

    async def on_interact_button_clicked(self, interaction: discord.Interaction):
        if self.on_interact_callback:
            await self.on_interact_callback(interaction)

    @property
    def cursor_position(self):
        letter = self.LETTERS[self.cursor_column]
        number = self.NUMBERS[self.cursor_row]
        return f"{letter}{number}"

    async def on_move_button_clicked(self, interaction: discord.Interaction):
        button_id = interaction.data["custom_id"]
        if button_id == "up_left":
            self.cursor_row -= 1
            self.cursor_column -= 1
        elif button_id == "left":
            self.cursor_column -= 1
        elif button_id == "down_left":
            self.cursor_row += 1
            self.cursor_column -= 1
        elif button_id == "up":
            self.cursor_row -= 1
        elif button_id == "down":
            self.cursor_row += 1
        elif button_id == "up_right":
            self.cursor_row -= 1
            self.cursor_column += 1
        elif button_id == "right":
            self.cursor_column += 1
        elif button_id == "down_right":
            self.cursor_row += 1
            self.cursor_column += 1
        else:
            logger.warning(f"Unknown button id: {button_id}")

        # Wrap around if necessary
        if self.cursor_row < 0:
            self.cursor_row = len(self.NUMBERS) - 1
        if self.cursor_row > len(self.NUMBERS) - 1:
            self.cursor_row = 0
        if self.cursor_column < 0:
            self.cursor_column = len(self.LETTERS) - 1
        if self.cursor_column > len(self.LETTERS) - 1:
            self.cursor_column = 0

        if self.on_cursor_change_callback:
            await self.on_cursor_change_callback(interaction)

    def add_buttons(self, view: ScenarioView):
        view.add_item(self.up_left)
        view.add_item(self.left)
        view.add_item(self.down_left)
        view.add_item(self.up)
        view.add_item(self.interact)
        view.add_item(self.down)
        view.add_item(self.up_right)
        view.add_item(self.right)
        view.add_item(self.down_right)
        view.add_item(self.exit_button)
        view.add_item(self.eat_button)
        view.add_item(self.next_button)

    def remove_buttons(self, view: ScenarioView):
        view.remove_item(self.up_left)
        view.remove_item(self.left)
        view.remove_item(self.down_left)
        view.remove_item(self.up)
        view.remove_item(self.interact)
        view.remove_item(self.down)
        view.remove_item(self.up_right)
        view.remove_item(self.right)
        view.remove_item(self.down_right)
        view.remove_item(self.exit_button)
        view.remove_item(self.eat_button)
        view.remove_item(self.next_button)
