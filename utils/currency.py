
from utils.emoji_map import EMOJI_MAP


def format_currency(value, currency=EMOJI_MAP["item:coin"]):
    real_value = value / 100
    return f"{real_value:.2f} {currency}"
