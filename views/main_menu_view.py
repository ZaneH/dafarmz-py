
import discord
from images.render import render_farm
from models.plots import FarmModel

from models.users import UserModel
from utils.embeds import create_embed_for_challenges, create_farm_embed, create_profile_embed
from views.challenges_view import ChallengesView
from views.command_center_view import CommandCenterView
from views.farm_view import FarmView
from views.profile_view import ProfileView
from views.robot_hq_view import RobotHQView


class MainMenuView(discord.ui.View):
    async def on_timeout(self):
        await self.message.edit(view=None)

    def __init__(self, timeout=120):
        super().__init__(timeout=timeout)

        # -- Categories --
        self.command_center_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Command Center",
            row=0,
        )
        self.command_center_button.callback = self.on_command_center_button_clicked
        self.add_item(self.command_center_button)

        self.robot_hq_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Robot HQ",
            row=1,
        )
        self.robot_hq_button.callback = self.on_robot_hq_button_clicked
        self.add_item(self.robot_hq_button)

        self.bunker_actions_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Bunker Actions",
            row=2,
        )
        self.bunker_actions_button.callback = self.on_bunker_actions_clicked
        self.add_item(self.bunker_actions_button)

        # -- Top 4 --

        # Command Center Buttons
        # Help, Profile, About, Vote
        self.help_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Help (Command List)",
            row=0,
        )
        self.help_button.callback = self.on_help_button_clicked
        self.add_item(self.help_button)

        self.profile_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Profile",
            row=0,
        )
        self.profile_button.callback = self.on_profile_button_clicked
        self.add_item(self.profile_button)

        self.about_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="About",
            row=0,
        )
        self.about_button.callback = self.on_help_button_clicked
        self.add_item(self.about_button)

        self.challenges_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Challenges",
            row=0,
        )
        self.challenges_button.callback = self.on_challenges_button_clicked
        self.add_item(self.challenges_button)

        # Robot HQ Buttons
        # Farming, explore, fish, battle
        self.farm_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Farm",
            row=1,
        )
        self.farm_button.callback = self.on_farm_button_clicked
        self.add_item(self.farm_button)

        self.explore_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Explore",
            row=1,
        )
        self.explore_button.callback = self.on_bunker_actions_clicked
        self.add_item(self.explore_button)

        self.fish_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Fish",
            row=1,
        )
        self.fish_button.callback = self.on_robot_hq_button_clicked
        self.add_item(self.fish_button)

        self.battle_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Battle",
            row=1,
        )
        self.battle_button.callback = self.on_robot_hq_button_clicked
        self.add_item(self.battle_button)

        # Bunker Buttons
        # Shop, craft, eat, upgrade, inventory
        self.shop_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Shop",
            row=2,
        )
        self.shop_button.callback = self.on_robot_hq_button_clicked
        self.add_item(self.shop_button)

        self.craft_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Craft",
            row=2,
        )
        self.craft_button.callback = self.on_robot_hq_button_clicked
        self.add_item(self.craft_button)

        self.eat_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Eat",
            row=2,
        )
        self.eat_button.callback = self.on_robot_hq_button_clicked
        self.add_item(self.eat_button)

        self.upgrade_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Upgrade",
            row=2,
        )
        self.upgrade_button.callback = self.on_robot_hq_button_clicked
        self.add_item(self.upgrade_button)

        self.vote_button = discord.ui.Button(
            label="Vote",
            row=4,
            url="https://top.gg/bot/1141161773983088640/vote",
            emoji="<:topgg:918280202398875758>"
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

    async def on_robot_hq_button_clicked(self, interaction: discord.Interaction):
        robot_hq = RobotHQView()
        await interaction.message.edit(embed=None, view=robot_hq)
        await interaction.response.defer()

    async def on_bunker_actions_clicked(self, interaction: discord.Interaction):
        await interaction.response.send_message("Explore button clicked!", ephemeral=True)

    async def on_help_button_clicked(self, interaction: discord.Interaction):
        await interaction.response.send_message("Profile button clicked!", ephemeral=True)

    async def on_challenges_button_clicked(self, interaction: discord.Interaction):
        user = await UserModel.find_by_discord_id(interaction.user.id)
        challenges_view = ChallengesView(user, back_button_row=4)
        embed = create_embed_for_challenges(
            interaction.user.display_name, user.challenges)
        await interaction.message.edit(embed=embed, view=challenges_view)
        await interaction.response.defer()

    async def on_profile_button_clicked(self, interaction: discord.Interaction):
        user = await UserModel.find_by_discord_id(interaction.user.id)
        embed = create_profile_embed(user, interaction.user)
        profile_view = ProfileView()
        await interaction.message.edit(
            embed=embed,
            view=profile_view
        )

        await interaction.response.defer()
