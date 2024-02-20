from models.yieldmodel import YieldModel
import random


def get_yield_with_odds(yield_: YieldModel) -> int:
    """
    Get the yield with odds factored in.
    Also use min_amount and max_amount if they are set.

    :param yield_: The yield to get.
    :return: The yield amount.
    """
    if yield_.min_amount != None and yield_.max_amount != None:
        return random.randint(yield_.min_amount, yield_.max_amount) if yield_.odds >= random.random() else 0

    return yield_.amount if yield_.odds >= random.random() else 0
