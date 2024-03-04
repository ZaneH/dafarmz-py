import discord


class SubmenuView(discord.ui.View):
    async def on_timeout(self):
        return await self.message.edit(view=None)

    def __init__(self, timeout=None, back_button_row=4):
        super().__init__(timeout=timeout)

        self.menu_depth = 0
        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="←",
            custom_id="back",
            row=back_button_row,
        )
        self.back_button.callback = self.on_back_button_clicked
        self.add_item(self.back_button)

    @property
    def should_main_menu(self):
        return self.menu_depth == 0

    async def on_back_button_clicked(self, interaction: discord.Interaction):
        from cogs.menu import create_main_menu_embed
        from views.main_menu_view import MainMenuView
        await interaction.response.edit_message(
            content="",
            embed=create_main_menu_embed(),
            view=MainMenuView(),
            files=[],
            attachments=[]
        )

    def readd_back_button(self):
        """
        Re-add the back button to the view
        """
        if self.back_button:
            self.remove_item(self.back_button)

        self.add_item(self.back_button)

    def add_menu_depth(self):
        """
        Add a depth to the menu

        This is used to keep track of how deep the menu is. Useful for
        customizing back button functionality.
        """
        self.menu_depth += 1

    def remove_menu_depth(self):
        """
        Remove a depth from the menu

        This is used to keep track of how deep the menu is. Useful for
        customizing back button functionality.
        """
        self.menu_depth = max(0, self.menu_depth - 1)
