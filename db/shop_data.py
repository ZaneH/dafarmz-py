from typing import List

from models.shop_items import ShopItemModel


class ShopData:
    def __init__(self):
        self.buyable_data = []
        self.all_shop_data = []
        self._instance = None

    @classmethod
    def buyable(cls) -> List[ShopItemModel]:
        return cls.get_instance().buyable_data

    @classmethod
    def all(cls) -> List[ShopItemModel]:
        return cls.get_instance().all_shop_data

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
