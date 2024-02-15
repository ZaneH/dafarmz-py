import discord


async def require_user(ctx: discord.context.ApplicationContext, user):
    """
    A helper function to check if a user has an account in the database.
    If the user does not have an account, a message will be sent to the ctx
    automatically.

    :param ctx: The context of the command.
    :param user: The user object from the database.
    :return: bool - True if the user exists, False if the user does not exist.
    """
    if not user:
        await ctx.respond("You don't have an account yet. Use `/setup` to start your farm.", ephemeral=True)
        return False

    # User exists
    return True
