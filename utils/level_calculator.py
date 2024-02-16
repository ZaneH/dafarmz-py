import math


def xp_required_for_level(level, X=0.07, Y=2):
    return math.floor((level / X) ** Y)


def level_based_on_xp(current_xp, X=0.07, Y=2):
    return math.floor(X * (current_xp ** (1 / Y)))


def next_level_xp(current_xp, X=0.07, Y=2):
    return xp_required_for_level(level_based_on_xp(current_xp) + 1, X, Y)
