
from db.shop_data import ShopData
from models.shop_items import ShopItemModel


def name_to_shop_item(name: str) -> ShopItemModel:
    """
    Get a shop item by its name.

    :param name: The name of the item
    :return: The shop item
    """
    shop_item = next((item for item in ShopData.all()
                     if item.name.lower() == name.lower()), None)
    if not shop_item:
        return None

    return shop_item


def key_to_shop_item(key: str) -> ShopItemModel:
    """
    Get a shop item by its key.

    :param key: The key of the item
    :return: The shop item
    """
    shop_item = next((item for item in ShopData.all()
                     if item.key.lower() == key.lower()), None)
    if not shop_item:
        return None

    return shop_item
