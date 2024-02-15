
import os
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

TOPGG_WEBHOOK_SECRET = os.getenv("TOPGG_WEBHOOK_SECRET")
router = APIRouter()


@router.get("/")
async def read_root():
    return {"status": "ok"}


@router.post("/webhook/topgg")
async def topgg_webhook(request: dict):
    user = request["user"]
    bot_id = request["bot"]

    logger.debug(f"Incoming top.gg webhook POST request: {request}")

    return {"success": True}
