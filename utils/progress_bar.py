import math


class ProgressBarEmoji:
    PEB = '<:PEB:1207983205286936607>'
    PFB = '<:PFB:1207984845758660618>'
    PFM = '<:PFM:1207983207455137843>'
    PHF = '<:PHF:1207983208549847100>'
    PEE = '<:PEE:1207983206423470090>'
    PEM = '<:PEM:1207983204040974377>'


def construct_progress_bar(current_xp, base_xp, xp_multiplier, total_segments=10):
    """
    Constructs a progress bar made of emojis based on the current XP within
    the current level for an exponential progression system.

    :param current_xp: The current XP of the player.
    :param base_xp: The base XP needed for the first level.
    :param xp_multiplier: The multiplier for each level's XP requirement.
    :param total_segments: The total number of segments in the progress bar, excluding the beginning and end pieces.
    :return: A string representing the progress bar.
    """
    # Determine the current level based on exponential progression
    current_level = math.floor(
        math.log(current_xp / base_xp) / math.log(xp_multiplier)) + 1

    # Calculate the total XP required to reach the current level
    xp_for_current_level = base_xp * (xp_multiplier ** (current_level - 1))

    # Calculate the total XP required to reach the next level
    xp_for_next_level = base_xp * (xp_multiplier ** current_level)

    # Calculate XP progress within the current level
    xp_into_current_level = current_xp - xp_for_current_level

    # Calculate the XP per segment for the current level
    xp_per_segment = (xp_for_next_level -
                      xp_for_current_level) / total_segments

    # Determine the number of filled segments
    filled_segments = int(xp_into_current_level // xp_per_segment)

    # Determine if there's a half-filled segment
    half_filled = xp_into_current_level % xp_per_segment > 0

    # Start with the beginning piece (filled if any progress, empty otherwise)
    progress_bar = ProgressBarEmoji.PFB if filled_segments > 0 or half_filled else ProgressBarEmoji.PEB

    # Add filled middle segments
    progress_bar += ProgressBarEmoji.PFM * filled_segments

    # Add a half-filled segment if needed
    if half_filled:
        progress_bar += ProgressBarEmoji.PHF
        filled_segments += 1  # Include the half-filled in the total filled count

    # Add empty middle segments
    empty_segments = total_segments - filled_segments
    progress_bar += ProgressBarEmoji.PEM * empty_segments

    # End with the closed and empty end piece
    progress_bar += ProgressBarEmoji.PEE

    return progress_bar
