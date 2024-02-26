from typing import List

from models.planets import PlanetModel


class PlanetsData:
    def __init__(self):
        self.all_planets: List[PlanetModel] = []
        self._instance = None

    @classmethod
    def all(cls) -> List[PlanetModel]:
        return cls.get_instance().all_planets

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_planet(cls, id: str) -> PlanetModel:
        instance = cls.get_instance()
        for planet in instance.all_planets:
            if planet.id == id:
                return planet

        return None

    @classmethod
    def get_biome(cls, planet_id: str, biome_index: int):
        planet = cls.get_planet(planet_id)
        if planet:
            return planet.biomes[biome_index]
        return None
