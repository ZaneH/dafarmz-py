from models.challenges import ChallengeOptionModel


def is_challenge_completed(challenge: ChallengeOptionModel) -> bool:
    """Check if a challenge is completed."""
    for action, goals in challenge.goal_stats.items():
        if isinstance(goals, dict):
            for item, goal_amount in goals.items():
                if challenge.progress.get(action, {}).get(item, 0) < goal_amount:
                    return False
        else:
            if challenge.progress.get(action, 0) < goals:
                return False

    return True
