from typing import List

from models.planets import PlanetModel


class PlanetsData:
    def __init__(self):
        self.all_planets = []
        self._instance = None

    @classmethod
    def all(cls) -> List[PlanetModel]:
        return cls.get_instance().all_planets

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
