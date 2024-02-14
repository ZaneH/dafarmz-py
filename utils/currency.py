def format_currency(value, currency="🪙"):
    real_value = value / 100
    return f"{real_value:.2f} {currency}"