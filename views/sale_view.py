from datetime import datetime
import discord

from utils.currency import format_currency
from utils.shop import key_to_shop_item


class SaleView(discord.ui.View):
    """
    A view for buying or selling items from the shop.
    Triggered with /buy or /sell
    """

    def __init__(self, shop_data=[], buy_or_sell="buy", timeout=None):
        """
        A view for buying or selling items from the shop.
        """

        super().__init__(timeout=timeout)

        self.on_purchase_callback = None

        self.buy_or_sell = buy_or_sell
        self.shop_data = shop_data
        self.selected_category = None
        self.selected_item = None
        self.quantity = 1
        self.cost_total = 0

        # Components
        self.items_select = None  # Item select dropdown
        self.qty_minus_five = None  # Quantity -5
        self.qty_minus_one = None  # Quantity -1
        self.qty_plus_one = None  # Quantity +1
        self.qty_plus_five = None  # Quantity +5
        self.qty_cancel = None  # Cancel button
        self.qty_confirm = None  # Confirm button

        self.item_type_select = discord.ui.Select(
            placeholder=f"Pick an item type...",
            custom_id="item_type_select",
            options=[
                discord.SelectOption(label="Seeds", value="seed"),
                discord.SelectOption(label="Plants", value="plant"),
                discord.SelectOption(label="Machines", value="machine"),
                discord.SelectOption(label="Tools", value="tool"),
                discord.SelectOption(label="Upgrades", value="upgrade")
            ],
            min_values=1, max_values=1,
            row=0
        )

        self.item_type_select.callback = self.select_category
        self.add_item(self.item_type_select)

    async def select_category(self, interaction):
        self.selected_category: str = interaction.data["values"][0]

        # Set default=True for the selected option
        for option in self.item_type_select.options:
            option.default = option.value == self.selected_category

        self.remove_item(self.items_select)

        self.items_select = discord.ui.Select(
            placeholder=f"Choose from the {self.selected_category}s to {self.buy_or_sell}",
            custom_id="items_select",
            options=[discord.SelectOption(label=item.name, value=item.key)
                     for item in self.shop_data if self.selected_category.lower() in item.key.lower()],
            min_values=1, max_values=1, row=1
        )

        self.items_select.callback = self.select_item_callback

        self.add_item(self.items_select)

        await self.message.edit(f"## Jason's Shop\nBrowsing {self.selected_category}s...", view=self)
        await interaction.response.defer()

    async def select_item_callback(self, interaction: discord.Interaction):
        self.selected_item = interaction.data["values"][0]
        self.selected_item_label = key_to_shop_item(self.selected_item).name

        # Set default=True for the selected option
        for option in self.items_select.options:
            option.default = option.value == interaction.data["values"][0]

        self.remove_item(self.qty_minus_five)
        self.remove_item(self.qty_minus_one)
        self.remove_item(self.qty_plus_one)
        self.remove_item(self.qty_plus_five)
        self.remove_item(self.qty_cancel)
        self.remove_item(self.qty_confirm)

        self.qty_minus_five = discord.ui.Button(
            style=discord.ButtonStyle.danger, label="-5", row=2,
            custom_id="qty_minus_five"
        )
        self.qty_minus_one = discord.ui.Button(
            style=discord.ButtonStyle.danger, label="-1", row=2,
            custom_id="qty_minus_one"
        )
        self.qty_plus_one = discord.ui.Button(
            style=discord.ButtonStyle.success, label="+1", row=2,
            custom_id="qty_plus_one"
        )
        self.qty_plus_five = discord.ui.Button(
            style=discord.ButtonStyle.success, label="+5", row=2,
            custom_id="qty_plus_five"
        )
        self.qty_cancel = discord.ui.Button(
            style=discord.ButtonStyle.danger, label="Cancel", row=3,
            custom_id="qty_cancel"
        )
        self.qty_confirm = discord.ui.Button(
            style=discord.ButtonStyle.success, label="Confirm", row=3,
            custom_id="qty_confirm"
        )

        self.qty_confirm.callback = self.confirm_purchase
        self.qty_cancel.callback = self.cancel_purchase
        self.qty_minus_five.callback = lambda x: self.update_quantity(x, -5)
        self.qty_minus_one.callback = lambda x: self.update_quantity(x, -1)
        self.qty_plus_one.callback = lambda x: self.update_quantity(x, 1)
        self.qty_plus_five.callback = lambda x: self.update_quantity(x, 5)

        self.add_item(self.qty_minus_five)
        self.add_item(self.qty_minus_one)
        self.add_item(self.qty_plus_one)
        self.add_item(self.qty_plus_five)
        self.add_item(self.qty_cancel)
        self.add_item(self.qty_confirm)

        verb = "Buying" if self.buy_or_sell == "buy" else "Selling"

        self.full_selected_item = key_to_shop_item(self.selected_item)

        self.update_cost_total()

        await self.message.edit(
            f"{verb} {self.quantity}x {self.selected_item_label} for {format_currency(self.cost_total)}",
            view=self
        )

        await interaction.response.defer()

    async def update_quantity(self, interaction, amount: int):
        verb = "Buying" if self.buy_or_sell == "buy" else "Selling"
        self.quantity = max(1, self.quantity + amount)

        self.update_cost_total()

        await self.message.edit(
            f"{verb} {self.quantity}x {self.selected_item_label} for {format_currency(self.cost_total)}",
            view=self
        )

        await interaction.response.defer()

    async def confirm_purchase(self, interaction: discord.Interaction):
        # Call the on_purchase_callback if it exists
        if self.on_purchase_callback:
            await self.on_purchase_callback(
                self,  # Pass the view instance
                self.selected_item,
                self.selected_item_label,
                self.quantity,
                self.cost_total
            )

        await interaction.response.defer()

    async def cancel_purchase(self, interaction):
        self.disable_all_items()
        await self.message.edit("Transaction cancelled.", view=self)

    def update_cost_total(self):
        if self.buy_or_sell == "buy":
            self.cost_total = self.full_selected_item.cost * self.quantity
        else:
            self.cost_total = self.full_selected_item.resell_price * self.quantity
