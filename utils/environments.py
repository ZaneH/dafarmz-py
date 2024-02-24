from enum import Enum


class Environment(Enum):
    DA_FIELDS = "da_fields"
    DA_FOREST = "da_forest"
    DA_MARSH = "da_marsh"
    DA_CAVES = "da_caves"
    DA_COLD = "da_cold"
    DA_JUNGLE = "da_jungle"
    DA_METEORSITE = "da_meteorsite"

    def __str__(self) -> str:
        return self.value.replace("_", " ").title()
