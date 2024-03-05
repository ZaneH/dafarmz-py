from models.users import UserModel
from utils.embeds import create_scenario_embed_and_file
from views.submenu_view import SubmenuView
from db.planets_data import PlanetsData
import discord


class SelectLocationView(SubmenuView):
    def __init__(self, unlocked_planets: list = [], timeout=None):
        super().__init__(timeout=timeout)

        self.selected_planet = None
        self.selected_biome_index = None

        planets = PlanetsData.get_planets_by_ids(unlocked_planets)

        self.planet_select = discord.ui.Select(
            placeholder="Select a planet",
            custom_id="planet_select",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=str(planet.name),
                    value=str(planet.id),
                )
                for planet in planets
            ],
        )
        self.planet_select.callback = self.on_planet_select
        self.add_item(self.planet_select)

        self.biome_select = None
        self.confirm_button = discord.ui.Button(
            label="Confirm",
            custom_id="confirm",
            style=discord.ButtonStyle.success,
            row=4,
        )
        self.confirm_button.callback = self.on_confirm_selection
        self.add_item(self.confirm_button)
        self.confirm_button.disabled = True

    async def on_planet_select(self, interaction: discord.Interaction):
        planet_id = interaction.data['values'][0]
        planet = PlanetsData.get_planet(planet_id)
        self.selected_planet = planet

        # add default=True to the selected planet
        for option in self.planet_select.options:
            option.default = option.value == planet_id

        self.add_biome_select_menu()

        await interaction.response.edit_message(view=self)

    def add_biome_select_menu(self):
        if self.biome_select:
            self.remove_item(self.biome_select)

        self.biome_select = discord.ui.Select(
            placeholder="Select a biome",
            custom_id="biome_select",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=str(biome.name),
                    value=str(index),
                )
                for index, biome in enumerate(self.selected_planet.biomes)
            ],
        )
        self.biome_select.callback = self.on_biome_select
        self.add_item(self.biome_select)

    async def on_biome_select(self, interaction: discord.Interaction):
        self.selected_biome_index = int(interaction.data['values'][0])

        # add default=True to the selected biome
        for option in self.biome_select.options:
            option.default = option.value == str(self.selected_biome_index)

        self.confirm_button.disabled = False
        await interaction.response.edit_message(view=self)

    async def on_confirm_selection(self, interaction: discord.Interaction):
        from views.scenario_view import ScenarioView

        profile = await UserModel.update_location(
            interaction.user.id,
            self.selected_planet.id,
            self.selected_biome_index,
        )

        scenario_view = ScenarioView(profile)
        (embed, file) = create_scenario_embed_and_file(profile)

        await interaction.response.edit_message(
            content="",
            embed=embed,
            file=file,
            view=scenario_view,
        )

    async def on_back_button_clicked(self, interaction: discord.Interaction):
        from views.scenario_view import ScenarioView

        profile = await UserModel.get_profile(interaction.user.id)

        scenario_view = ScenarioView(profile)
        (embed, file) = create_scenario_embed_and_file(profile)

        await interaction.response.edit_message(
            content="",
            embed=embed,
            file=file,
            view=scenario_view,
        )
