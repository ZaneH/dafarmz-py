import math


def xp_for_next_level(current_xp, base_xp=100, level_multiplier=1.5):
    """
    Calculate the XP needed for the next level.

    :param current_xp: The current total XP of the player.
    :param base_xp: The base XP needed for the first level.
    :param xp_increase_per_level: The additional XP needed for each subsequent level (for linear progression).
    :param level_multiplier: The multiplier for each level's XP requirement (for exponential progression).
    :return: The total XP needed for the next level.
    """
    current_level = (current_xp // base_xp)
    xp_for_next_level = base_xp * (level_multiplier ** current_level)

    return xp_for_next_level


def current_level(current_xp, base_xp=100, xp_multiplier=1.5):
    """
    Calculates the current level of a player based on exponential progression.

    :param current_xp: The current total XP of the player.
    :param base_xp: The base XP needed for the first level.
    :param xp_multiplier: The multiplier for each level's XP requirement.
    :return: The current level of the player.
    """
    if current_xp < base_xp:
        return 1  # Assuming the player starts at level 1
    level = math.floor(math.log(current_xp / base_xp) /
                       math.log(xp_multiplier)) + 1
    return level
