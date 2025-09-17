from fastapi import APIRouter, Request, Header
import asyncio
from commands.proxy_command import ProxyCommand
from core.queue_manager import enqueue
from typing import Optional

router = APIRouter()

@router.get("/proxy/score")
async def proxy_score(
    cpf: str,
    client_id: str = Header(...)
):
    params = {"cpf": cpf}
    headers = {"client-id": client_id}

    cmd = ProxyCommand(params=params, headers=headers)

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    if not enqueue((cmd, future)):
        return {"error": "Queue Full - request dropped"}

    return await future
