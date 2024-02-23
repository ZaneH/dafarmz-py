from enum import Enum


class Environment(Enum):
    BARREN_WASTELANDS = "barren_wastelands"
    GRASSLAND = "grassland"
    CO2_GREENHOUSE = "co2_greenhouse"
    CAVERNOUS_CAVES = "cavernous_caves"
    RADIOACTIVE_METEOR_SITE = "radioactive_meteor_site"
    ROCKY_RIVERS = "rocky_rivers"
    ARCTIC_WASTELAND = "arctic_wasteland"
    GIANT_JUNGLE = "giant_jungle"

    def __str__(self) -> str:
        if self == Environment.CO2_GREENHOUSE:
            return "CO2 Greenhouse"

        return self.value.replace("_", " ").title()
