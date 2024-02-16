from typing import List

from models.shop import ShopModel


class ShopData:
    def __init__(self):
        self.shop_data = []
        self._instance = None

    @classmethod
    def data(cls) -> List[ShopModel]:
        return cls.get_instance().shop_data

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
