from pydantic import BaseModel


class YieldModel(BaseModel):
    """
    Represents a singular yield.
    """
    amount: int = 0
    xp: int = 0
