from typing import Optional
from pydantic import BaseModel


class YieldModel(BaseModel):
    """
    Represents a singular yield.
    """
    odds: Optional[float] = 1.0  # The odds of this yield occurring
    amount: int = 0  # The amount of the yield
    min_amount: Optional[int] = None  # The minimum amount of the yield
    max_amount: Optional[int] = None  # The maximum amount of the yield
    xp: int = 0  # The amount of xp earned from the yield

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
