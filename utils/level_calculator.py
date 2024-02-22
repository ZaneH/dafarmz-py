"""
# Helper functions for calculating levels and XP.
# ---
# Math based on: https://blog.jakelee.co.uk/converting-levels-into-xp-vice-versa/
# Formula: (level/x)^y
# XP = (level/0.07)^2
# level = 0.07 * √XP
"""
import math


def level_to_xp(level, X=0.07, Y=2):
    return math.floor((level / X) ** Y)


def xp_to_level(current_xp, X=0.07, Y=2):
    """
    Calculate the level based on the current XP starting at level 1.

    :param current_xp: The current XP.
    :param X: The X value for the formula.
    :param Y: The Y value for the formula."""
    return math.floor(X * (current_xp ** (1 / Y)))


def next_level_xp(current_xp, X=0.07, Y=2):
    return level_to_xp(xp_to_level(current_xp) + 1, X, Y)
