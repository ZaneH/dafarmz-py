
import hmac
import os
from typing import Annotated
from fastapi import APIRouter, Header
import logging

from models.users import UserModel

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def read_root():
    return {"status": "ok"}


@router.post("/webhook/topgg")
async def topgg_webhook(
    request: dict,
    authorization: Annotated[str | None, Header()] = None
):
    user_id = request["user"]
    bot_id = request["bot"]
    type = request["type"]
    isWeekend = request.get("isWeekend", False)
    TOPGG_WEBHOOK_SECRET = os.getenv("TOPGG_WEBHOOK_SECRET")

    if type != "upvote":
        logger.debug(f"Received top.gg webhook POST request with type {type}")
        return {"success": True}

    if not hmac.compare_digest(authorization, TOPGG_WEBHOOK_SECRET):
        logger.warning(
            f"Unauthorized top.gg webhook POST request from {user_id} for bot {bot_id}")
        return {"success": False}

    logger.debug(f"Incoming top.gg webhook POST request: {request}")

    user = await UserModel.get_profile(user_id)
    if not user:
        logger.warning(
            f"User {user_id} not found for top.gg vote")
        return {"success": False}

    bonus_coins = 500

    if isWeekend:
        bonus_coins *= 2

    user.balance += bonus_coins
    await user.save()

    logger.info(
        f"User {user_id} has voted for bot {bot_id} and received the bonus. New balance: {user.balance}")

    return {"success": True}
