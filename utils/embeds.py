import discord

from db.shop_data import ShopData
from models.challenges import ChallengesModel
from utils.currency import format_currency
from utils.emoji_map import EMOJI_MAP
from utils.progress_bar import construct_normal_progrss_bar


def goal_completion_percentage(progress, goal_amount):
    """Calculate the completion percentage for a single goal."""
    return (progress / goal_amount) * 100 if goal_amount else 0


def create_embed_for_challenges(name: str, challenges: ChallengesModel):
    embed = discord.Embed(
        title=f"{name}'s Challenges",
        color=discord.Color.embed_background()
    )

    embed.add_field(
        name="Last Refreshed",
        value=challenges.last_refreshed_at.strftime("%b %d, %Y %I:%M %p"),
        inline=False
    )

    active_challenges = sum(option.accepted for option in challenges.options)
    max_active = challenges.max_active

    embed.add_field(
        name="Active Challenges",
        value=f"{active_challenges}/{max_active}",
        inline=False
    )

    shop_data = ShopData.all()
    for option in challenges.options:
        challenge_rewards = ""
        for reward_key, amount in option.rewards.items():
            reward_shop_item = next(
                (item for item in shop_data if item.key == reward_key), None)
            if reward_shop_item:
                challenge_rewards += f"{EMOJI_MAP.get(reward_shop_item.key, '')} {reward_shop_item.name}: {amount}\n"

        title = f"{option.description} {'(Active)' if option.accepted else ''}"
        value_text = (challenge_rewards if challenge_rewards else 'None')

        if option.accepted:
            # action: "harvest", "plant", etc.
            for action, goals in option.goal_stats.items():
                if isinstance(goals, dict):
                    for item, goal_amount in goals.items():
                        current_progress = option.progress.get(
                            action, {}
                        ).get(item, 0)

                        percentage = min(100, goal_completion_percentage(
                            current_progress, goal_amount
                        ))

                        progress_bar = construct_normal_progrss_bar(
                            percentage, 5
                        )

                        value_text = f"**{percentage:.2f}%** {progress_bar}\n{value_text}"
                else:
                    raise ValueError(
                        "Goal stats must be a dictionary of action: {item: goal_amount} pairs.")

        embed.add_field(name=title, value=value_text, inline=False)

    return embed


def create_shop_embed(shop_data):
    embed = discord.Embed(title="Jason's Shop",
                          color=discord.Color.blurple())

    embed.set_thumbnail(url="https://i.imgur.com/3CQRKGY.png")
    for item in shop_data:
        embed.add_field(
            name=f"{EMOJI_MAP.get(item.key, '')} {item.name}",
            value=f"{EMOJI_MAP['ui:reply']} {format_currency(item.cost)}",
            inline=False
        )

    return embed
