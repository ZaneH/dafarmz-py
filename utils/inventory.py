from models.user import UserModel


def get_amount_in_inventory(profile: UserModel, item_key: str) -> int:
    """Get the amount of an item in the user's inventory."""
    return profile.inventory.get(item_key, 0)
