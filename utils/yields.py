from typing import Dict
from models.yields import YieldModel
import random
from utils.emoji_map import EMOJI_MAP

from utils.shop import key_to_shop_item


def get_yield_with_odds(yield_: YieldModel) -> int:
    """
    Get the yield as a number with odds factored in.
    Also use min_amount and max_amount if they are set.

    :param yield_: The yield to get.
    :return: The yield amount.
    """
    if yield_.min_amount != None and yield_.max_amount != None:
        return random.randint(yield_.min_amount, yield_.max_amount) if yield_.odds >= random.random() else 0

    return yield_.amount if yield_.odds >= random.random() else 0


def harvest_yield_to_list(harvest_yield: Dict[str, YieldModel]) -> str:
    """
    Format a yield into a list of bullet point items.

    :param yield_: The yield to format.
    :return: The formatted yield.
    """
    yields_ = []
    for item, yields in harvest_yield.items():
        shop_item = key_to_shop_item(item)
        if shop_item:
            yields_.append(
                f"- {EMOJI_MAP[item]} {yields.amount}x {shop_item.name}")

    return "\n".join(yields_) if yields_ else "Nothing"
