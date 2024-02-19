from datetime import datetime
import discord

from models.user import UserModel
from utils.embeds import create_embed_for_challenges


class ChallengesView(discord.ui.View):
    """
    A view that allows a user to view their challenge, refresh their challenges,
    select a challenge, accept a challenge, view their progress, and claim rewards.
    Triggered with /challenges
    """
    async def on_timeout(self) -> None:
        self.clear_items()
        await self.message.edit(
            content="",
            view=None
        )

    def create_challenge_option_select(self):
        selection_options = []
        for i, option in enumerate(self.challenges.options):
            selection_options.append(discord.SelectOption(
                label=option.description,
                value=str(i)
            ))

        select = discord.ui.Select(
            placeholder="Select a challenge",
            row=0,
            options=selection_options
        )

        select.callback = self.on_challenge_option_selected
        return select

    def __init__(self, profile: UserModel, timeout=120):
        super().__init__(timeout=timeout)

        self.profile = profile
        self.challenges = profile.challenges

        self.selected_option = None
        self.challenge_option_select = self.create_challenge_option_select()
        if len(self.challenges.options) > 0:
            self.add_item(self.challenge_option_select)

        self.accept_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Accept",
            row=4,
        )

        self.refresh_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Refresh",
            row=4,
        )

        self.accept_button.callback = self.on_accept_button_clicked
        self.refresh_button.callback = self.on_refresh_button_clicked

        can_refresh = (datetime.utcnow(
        ) - self.profile.challenges.last_refreshed_at).total_seconds() > 86400
        if can_refresh:
            self.add_item(self.refresh_button)

    async def on_challenge_option_selected(self, interaction: discord.Interaction):
        self.remove_item(self.refresh_button)

        self.selected_option = int(interaction.data["values"][0])
        self.add_item(self.accept_button)

        # set default=True for the selected option
        for option in self.challenge_option_select.options:
            option.default = option.value == interaction.data["values"][0]

        await interaction.message.edit(view=self)
        await interaction.response.defer()

    async def on_accept_button_clicked(self, interaction: discord.Interaction):
        new_user = await UserModel.accept_challenge(self.profile.discord_id, self.selected_option)
        self.profile = new_user
        self.challenges = new_user.challenges
        self.clear_items()
        await interaction.message.edit(
            embed=create_embed_for_challenges(
                interaction.user.display_name, self.challenges),
            view=self
        )

        await interaction.response.defer()

    async def on_refresh_button_clicked(self, interaction: discord.Interaction):
        try:
            new_user = await UserModel.refresh_challenges(
                self.profile.discord_id, self.profile.stats.get("xp", 0),
                self.profile.challenges.last_refreshed_at
            )

            self.profile = new_user
            self.challenges = new_user.challenges

            self.clear_items()
            if len(self.challenges.options) > 0:
                self.challenge_option_select = self.create_challenge_option_select()
                self.add_item(self.challenge_option_select)

            await interaction.message.edit(
                embed=create_embed_for_challenges(
                    interaction.user.display_name, self.challenges),
                view=self
            )

            await interaction.response.defer()
        except Exception as e:
            await interaction.response.edit_message(
                content=str(e),
                view=self
            )
