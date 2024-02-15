import discord


class BuyView(discord.ui.View):
    def __init__(self, shop_data):
        super().__init__()

        self.shop_data = shop_data
        self.selected_type = None
        self.selected_item = None
        self.quantity = 1

        # Views
        self.items_select = None
        self.qty_minus_five = None
        self.qty_minus_one = None
        self.qty_plus_one = None
        self.qty_plus_five = None
        self.qty_cancel = None
        self.qty_confirm = None

    @discord.ui.select(placeholder="What type of item do you want to buy?",
                       options=[
                           discord.SelectOption(label="Plants", value="plant"),
                           discord.SelectOption(
                               label="Machines", value="machine"),
                           discord.SelectOption(label="Tools", value="tool"),
                           discord.SelectOption(
                               label="Upgrades", value="upgrade")
                       ],
                       min_values=1, max_values=1,
                       row=0)
    async def select_type(self, select, interaction):
        self.selected_type = select.values[0]

        self.remove_item(self.items_select)

        self.items_select = discord.ui.Select(
            placeholder=f"Choose from the {self.selected_type}s to buy",
            options=[discord.SelectOption(label=item.name, value=item.name)
                     for item in self.shop_data if item.type == self.selected_type],
            min_values=1, max_values=1, row=1
        )

        self.items_select.callback = self.select_item

        self.add_item(self.items_select)

        await self.message.edit(f"## Shop\nBrowsing {self.selected_type}s...", view=self)
        await interaction.response.defer()

    async def select_item(self, interaction):
        self.selected_item = interaction.data["values"][0]

        self.remove_item(self.qty_minus_five)
        self.remove_item(self.qty_minus_one)
        self.remove_item(self.qty_plus_one)
        self.remove_item(self.qty_plus_five)
        self.remove_item(self.qty_cancel)
        self.remove_item(self.qty_confirm)

        self.qty_minus_five = discord.ui.Button(
            style=discord.ButtonStyle.danger, label="-5", row=2)
        self.qty_minus_one = discord.ui.Button(
            style=discord.ButtonStyle.danger, label="-1", row=2)
        self.qty_plus_one = discord.ui.Button(
            style=discord.ButtonStyle.success, label="+1", row=2)
        self.qty_plus_five = discord.ui.Button(
            style=discord.ButtonStyle.success, label="+5", row=2)
        self.qty_cancel = discord.ui.Button(
            style=discord.ButtonStyle.danger, label="Cancel", row=3)
        self.qty_confirm = discord.ui.Button(
            style=discord.ButtonStyle.success, label="Confirm", row=3)

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

        await self.message.edit(f"Buying {self.quantity}x {self.selected_item}...", view=self)
        await interaction.response.defer()

    async def update_quantity(self, interaction, amount: int):
        self.quantity = max(1, self.quantity + amount)
        await self.message.edit(f"Buying {self.quantity}x {self.selected_item}...", view=self)
        await interaction.response.defer()

    async def confirm_purchase(self, interaction):
        await self.message.edit(f"Purchased {self.quantity}x {self.selected_item}!", view=None)

    async def cancel_purchase(self, interaction):
        await self.message.edit("Purchase cancelled.", view=None)
