import discord

from models.user import UserModel
from utils.embeds import create_embed_for_challenges


class ChallengesView(discord.ui.View):
    async def on_timeout(self) -> None:
        self.clear_items()
        await self.message.edit(
            content="",
            view=None
        )

    def __init__(self, profile: UserModel, timeout=120):
        super().__init__(timeout=timeout)

        self.profile = profile
        self.challenges = profile.challenges

        self.daily_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Daily",
        )

        options = []
        for i, option in enumerate(self.challenges.options):
            options.append(discord.SelectOption(
                label=option.description,
                value=str(i)
            ))

        self.challenge_option_select = discord.ui.Select(
            placeholder="Select a challenge",
            row=0,
            options=options
        )

        self.selected_option = None
        self.challenge_option_select.callback = self.on_challenge_option_selected

        self.accept_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Accept",
            row=4,
        )

        self.accept_button.callback = self.on_accept_button_clicked

        self.add_item(self.challenge_option_select)

    async def on_challenge_option_selected(self, interaction: discord.Interaction):
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
