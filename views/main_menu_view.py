
import discord
from images.render import render_farm
from models.planets import build_biome_image_path
from models.plots import FarmModel

from models.users import UserModel
from utils.embeds import create_command_list_embed, create_embed_for_challenges, create_farm_embed, create_planet_embed, create_profile_embed, create_scenario_embed_and_file, create_shop_embed, inventory_to_embed
from utils.emoji_map import EMOJI_MAP
from utils.users import require_user
from views.challenges_view import ChallengesView
from views.command_center_view import CommandCenterView
from views.farm_view import FarmView
from views.planets_view import PlanetsView
from views.profile_view import ProfileView
from views.scenario_view import ScenarioView
from views.shop_view import ShopView
from views.submenu_view import SubmenuView


class MainMenuView(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

        # -- Categories --
        self.command_center_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Command Center",
            custom_id="command_center",
            row=0,
        )
        self.command_center_button.callback = self.on_command_center_button_clicked
        self.add_item(self.command_center_button)

        self.odyssey_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Odyssey",
            custom_id="odyssey",
            row=1,
        )
        self.odyssey_button.callback = self.on_odyssey_button_clicked
        self.add_item(self.odyssey_button)

        self.colony_actions_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Colony Actions",
            custom_id="colony_actions",
            row=2,
        )
        self.colony_actions_button.callback = self.on_colony_actions_clicked
        self.add_item(self.colony_actions_button)

        # -- Top 4 --

        # Command Center Buttons
        # Help, Profile, About, Vote
        self.help_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Help (Command List)",
            custom_id="help_command_list",
            row=0,
        )
        self.help_button.callback = self.on_help_button_clicked
        self.add_item(self.help_button)

        self.profile_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Profile",
            custom_id="profile",
            row=0,
        )
        self.profile_button.callback = self.on_profile_button_clicked
        self.add_item(self.profile_button)

        self.challenges_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Challenges",
            custom_id="challenges",
            row=0,
        )
        self.challenges_button.callback = self.on_challenges_button_clicked
        self.add_item(self.challenges_button)

        self.about_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="About",
            custom_id="about",
            row=0,
        )
        self.about_button.callback = self.on_about_button_clicked
        self.add_item(self.about_button)

        # Robot HQ Buttons
        # Farming, explore, fish, battle
        self.farm_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Farm",
            custom_id="farm",
            row=1,
        )
        self.farm_button.callback = self.on_farm_button_clicked
        self.add_item(self.farm_button)

        self.explore_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Explore",
            custom_id="explore",
            row=1,
        )
        self.explore_button.callback = self.on_explore_button_clicked
        self.add_item(self.explore_button)

        self.fish_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Fish",
            custom_id="fish",
            row=1,
        )
        self.fish_button.callback = self.on_odyssey_button_clicked
        self.add_item(self.fish_button)

        self.battle_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Battle",
            custom_id="battle",
            row=1,
        )
        self.battle_button.callback = self.on_odyssey_button_clicked
        self.add_item(self.battle_button)

        # Bunker Buttons
        # Shop, craft, eat, upgrade, inventory
        self.shop_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Shop",
            custom_id="shop",
            row=2,
        )
        self.shop_button.callback = self.on_shop_button_clicked
        self.add_item(self.shop_button)

        self.craft_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Craft",
            custom_id="craft",
            row=2,
        )
        self.craft_button.callback = self.on_odyssey_button_clicked
        self.add_item(self.craft_button)

        self.inventory_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Inventory",
            custom_id="inventory",
            row=2,
        )
        self.inventory_button.callback = self.on_inventory_button_clicked
        self.add_item(self.inventory_button)

        self.upgrade_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Upgrade",
            custom_id="upgrade",
            row=2,
        )
        self.upgrade_button.callback = self.on_odyssey_button_clicked
        self.add_item(self.upgrade_button)

        self.vote_button = discord.ui.Button(
            label="Vote",
            row=4,
            url="https://top.gg/bot/1141161773983088640/vote",
            emoji=f"{EMOJI_MAP['emote:topgg']}"
        )
        self.add_item(self.vote_button)

    async def on_command_center_button_clicked(self, interaction: discord.Interaction):
        command_center = CommandCenterView()
        await interaction.message.edit(embed=None, view=command_center)
        await interaction.response.defer()

    async def on_farm_button_clicked(self, interaction: discord.Interaction):
        farm = await FarmModel.find_by_discord_id(interaction.user.id)
        farm_view = FarmView(farm, interaction.user, back_button_row=0)
        embed = create_farm_embed(interaction.user.display_name)
        await interaction.message.edit(embed=embed, view=farm_view, files=[await render_farm(farm)])
        await interaction.response.defer()

    async def on_odyssey_button_clicked(self, interaction: discord.Interaction):
        planets_view = PlanetsView()
        (embed, file) = planets_view.create_embed_and_file()

        await interaction.message.edit(
            embed=embed,
            view=planets_view,
            file=file
        )

        await interaction.response.defer()

    async def on_colony_actions_clicked(self, interaction: discord.Interaction):
        pass

    async def on_explore_button_clicked(self, interaction: discord.Interaction):
        profile = await UserModel.get_profile(interaction.user.id)
        scenario_view = ScenarioView(profile)
        scenario_view.profile = profile
        (embed, file) = create_scenario_embed_and_file(profile)
        await interaction.message.edit(
            embed=embed,
            file=file,
            view=scenario_view
        )
        await interaction.response.defer()

    async def on_help_button_clicked(self, interaction: discord.Interaction):
        back_view = SubmenuView()
        embed = create_command_list_embed()
        await interaction.message.edit(embed=embed, view=back_view)
        await interaction.response.defer()

    async def on_challenges_button_clicked(self, interaction: discord.Interaction):
        user = await UserModel.get_profile(interaction.user.id)
        challenges_view = ChallengesView(user)
        embed = create_embed_for_challenges(
            interaction.user.display_name, user.challenges)
        await interaction.message.edit(embed=embed, view=challenges_view)
        await interaction.response.defer()

    async def on_profile_button_clicked(self, interaction: discord.Interaction):
        user = await UserModel.get_profile(interaction.user.id)
        embed = create_profile_embed(user, interaction.user)
        profile_view = ProfileView()
        await interaction.message.edit(
            embed=embed,
            view=profile_view
        )

        await interaction.response.defer()

    async def on_shop_button_clicked(self, interaction: discord.Interaction):
        shop_view = ShopView()
        embed = create_shop_embed(shop_view.pagination.get_page())
        await interaction.response.edit_message(
            content="",
            embed=embed,
            view=shop_view,
            files=[],
            attachments=[]
        )

    async def on_inventory_button_clicked(self, interaction: discord.Interaction):
        profile = await UserModel.get_profile(interaction.user.id)
        back_view = SubmenuView()
        return await interaction.response.edit_message(
            embed=inventory_to_embed(profile.inventory),
            view=back_view
        )

    async def on_about_button_clicked(self, interaction: discord.Interaction):
        pass
