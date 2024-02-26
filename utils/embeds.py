import random
import discord

from models.challenges import ChallengesModel
from models.planets import PlanetModel
from models.shop_items import ShopItemModel
from models.users import UserModel
from utils.currency import format_currency
from utils.emoji_map import EMOJI_MAP
from utils.inventory import get_amount_in_inventory
from utils.level_calculator import next_level_xp
from utils.progress_bar import construct_normal_progrss_bar, construct_xp_progress_bar
from utils.shop import key_to_shop_item


def create_farm_embed(farm_owner_name: str):
    embed = discord.Embed(
        title=f"{farm_owner_name}'s Farm",
        color=discord.Color.embed_background()
    )

    return embed


def create_scenario_embed(profile: UserModel):
    embed = discord.Embed(
        title=f"Go Exploring",
        color=discord.Color.embed_background()
    )

    embed.add_field(
        name="Available Robots",
        value=f"{EMOJI_MAP['ui:reply']} {get_amount_in_inventory(profile, 'item:robot')}",
        inline=False
    )

    return embed


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
        value=f"` {active_challenges} / {max_active} `",
        inline=False
    )

    for option in challenges.options:
        challenge_rewards = ""
        for reward_key, amount in option.rewards.items():
            reward_shop_item = key_to_shop_item(reward_key)
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

                        percentage = goal_completion_percentage(
                            current_progress, goal_amount
                        )

                        progress_bar = construct_normal_progrss_bar(
                            percentage, 5
                        )

                        value_text = f"**{percentage:.2f}%** {progress_bar}\n{value_text}"
                else:
                    raise ValueError(
                        "Goal stats must be a dictionary of action: {item: goal_amount} pairs.")

        embed.add_field(name=title, value=value_text, inline=False)

    return embed


def create_shop_embed(shop_items: list[ShopItemModel]):
    embed = discord.Embed(title="Jason's Shop",
                          color=discord.Color.blurple())

    embed.set_thumbnail(url="https://i.imgur.com/3CQRKGY.png")
    for item in shop_items:
        embed.add_field(
            name=f"{EMOJI_MAP.get(item.key, '')} {item.name}",
            value=f"{EMOJI_MAP['ui:reply']} {format_currency(item.cost)}",
            inline=False
        )

    return embed


def create_shop_item_embed(item: ShopItemModel, file: discord.File):
    embed = discord.Embed(
        title=item.name,
        description=f"> *{item.description if item.description else 'No description available.'}*",
        color=discord.Color.embed_background(),
    )

    if file:
        embed.set_thumbnail(url=f"attachment://{file.filename}")
    else:
        embed.set_thumbnail(url="https://i.imgur.com/3CQRKGY.png")

    embed.add_field(
        name="Cost", value=f"{format_currency(item.cost)}", inline=True)
    embed.add_field(name="Level Required",
                    value=f"{item.level_required}", inline=True)

    if item.environment_buffs:
        buffs = ""
        for env, buff in item.environment_buffs.items():
            buff_emoji = "✅"
            if buff == 0:
                buff_emoji = "❌"
            elif buff < 1:
                buff_emoji = "⏬"
            elif buff > 1:
                buff_emoji = "⏫"

            buffs += f"{str(env)}: {buff_emoji}\n"

        embed.add_field(name="Environment Buffs", value=buffs, inline=False)

    return embed


def create_profile_embed(profile: UserModel, discord_user: discord.User):
    random_tip = random.choice([
        "Use </inventory:1207866795147657219> to view your inventory.",
        "Use </stats:1207963367864795207> to view statistics about your farm.",
    ])

    xp = profile.stats.get("xp", 0)
    next_milestone = next_level_xp(xp)
    embed = discord.Embed(
        title=f"{discord_user.display_name}'s Profile :farmer:",
        description=f"""**Balance**: {format_currency(profile.balance)}
**Joined**: {profile.created_at.strftime("%b %d, %Y")}

**Level {profile.current_level}** – {xp}/{next_milestone} XP:
{construct_xp_progress_bar(int(xp), 8)}

{random_tip}""",
        color=discord.Color.embed_background(),
    )

    embed.set_thumbnail(url=discord_user.avatar.url)
    return embed


def create_farm_stats_embed(profile: UserModel):
    embed = discord.Embed(
        title="Farm Statistics",
        description=f"**Balance**: {format_currency(profile.balance)}",
        color=discord.Color.embed_background()
    )

    planted_count = profile.stats.get("plant", {}).get("count", 0)
    harvest_count = profile.stats.get("harvest", {}).get("count", 0)

    embed.add_field(
        name="Planted",
        value=f"{EMOJI_MAP['emote:potted']} {planted_count}",
        inline=True
    )

    embed.add_field(
        name="Harvests",
        value=f"{EMOJI_MAP['tool:harvest']} {harvest_count}",
        inline=True
    )

    return embed


def create_explore_stats_embed(profile: UserModel):
    embed = discord.Embed(
        title="Explore Statistics",
        description=f"**Balance**: {format_currency(profile.balance)}",
        color=discord.Color.embed_background()
    )

    harvest_count = profile.stats.get(
        "scenario", {}).get("harvest", {}).get("count", 0)
    xp_earned_harvesting = profile.stats.get(
        "scenario", {}).get("harvest", {}).get("xp", 0)

    embed.add_field(
        name="Harvests",
        value=f"{EMOJI_MAP['tool:harvest']} {harvest_count}",
        inline=True
    )

    embed.add_field(
        name="XP Earned",
        value=f"{EMOJI_MAP['item:xp']} {xp_earned_harvesting}",
        inline=True
    )

    return embed


def create_command_list_embed():
    embed = discord.Embed(
        title="Help (Command List)",
        description="Here are the commands you can use to interact with the bot.",
        color=discord.Color.embed_background()
    )

    embed.add_field(
        name="🏠 Main Menu",
        value="`/menu`",
        inline=False
    )

    embed.add_field(
        name="🌾 Farm",
        value="`/farm`",
        inline=False
    )

    embed.add_field(
        name="🛒 Shop",
        value="`/shop`",
        inline=False
    )

    embed.add_field(
        name="📊 Stats",
        value="`/stats`",
        inline=False
    )

    embed.add_field(
        name="🎮 Challenges",
        value="`/challenges`",
        inline=False
    )

    embed.add_field(
        name="🤖 Robot HQ",
        value="`/robot`",
        inline=False
    )

    embed.add_field(
        name="🔍 Explore",
        value="`/explore`",
        inline=False
    )

    embed.add_field(
        name="🎣 Fish",
        value="`/fish`",
        inline=False
    )

    embed.add_field(
        name="🔫 Battle",
        value="`/battle`",
        inline=False
    )

    embed.add_field(
        name="🏚️ Bunker",
        value="`/bunker`",
        inline=False
    )

    embed.add_field(
        name="🍔 Eat",
        value="`/eat`",
        inline=False
    )

    embed.add_field(
        name="🗳️ Vote",
        value="`/vote`",
        inline=False
    )

    return embed


def create_planet_embed(planet: PlanetModel, file: discord.File = None):
    embed = discord.Embed(
        title=f"{planet.name}",
        description=f"{planet.description}",
        color=discord.Color.embed_background()
    )

    if file:
        embed.set_thumbnail(url=f"attachment://{file.filename.split('/')[-1]}")

    return embed
