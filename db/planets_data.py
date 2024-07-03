from typing import List

from models.planets import PlanetModel
from models.pyobjectid import PyObjectId
from utils.level_calculator import xp_to_level


class PlanetsData:
    def __init__(self):
        self.all_planets: List[PlanetModel] = []
        self._instance = None

    @classmethod
    def get_planets(cls) -> List[PlanetModel]:
        """
        Get all the planets in the game

        :return: List[PlanetModel]
        """
        return cls.get_instance().all_planets

    @classmethod
    def get_planets_by_ids(cls, ids: List[PyObjectId]) -> List[PlanetModel]:
        """
        Get all the planets in the game

        :return: List[PlanetModel]
        """
        return [planet for planet in cls.get_instance().all_planets if planet.id in ids]

    @classmethod
    def get_planet(cls, id: str) -> PlanetModel:
        """
        Get a planet by id

        :param id: str
        :return: PlanetModel
        """
        instance = cls.get_instance()
        for planet in instance.all_planets:
            if str(planet.id) == str(id):
                return planet

        return None

    @classmethod
    def get_biome(cls, planet_id: str, biome_index: int):
        """
        Get a biome by index

        :param planet_id: str
        :param biome_index: int
        :return: BiomeModel
        """
        planet = cls.get_planet(planet_id)
        if planet:
            return planet.biomes[biome_index]
        return None

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
