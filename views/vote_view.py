import discord
from utils.emoji_map import EMOJI_MAP

from views.submenu_view import SubmenuView


class VoteView(SubmenuView):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

        self.vote_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Vote",
            row=0,
            url="https://top.gg/bot/1141161773983088640/vote",
            emoji=f"{EMOJI_MAP['emote:topgg']}"
        )
        self.add_item(self.vote_button)