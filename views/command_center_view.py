import discord


class CommandCenterView(discord.ui.View):
    async def on_timeout(self):
        return await self.message.edit(view=None)

    def __init__(self, timeout=120):
        super().__init__(timeout=timeout)

        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="←",
            row=0,
        )
        self.back_button.callback = self.on_back_button_clicked
        self.add_item(self.back_button)

    async def on_back_button_clicked(self, interaction: discord.Interaction):
        from cogs.menu import create_main_menu_embed
        from views.main_menu_view import MainMenuView
        await interaction.response.edit_message(embed=create_main_menu_embed(), view=MainMenuView())
