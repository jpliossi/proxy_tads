from fastapi import APIRouter, Request
import asyncio
from commands.proxy_command import ProxyCommand
from core.queue_manager import enqueue

router = APIRouter()

@router.get("/proxy/score")
async def proxy_score(request: Request):
    params = dict(request.query_params)
    cmd = ProxyCommand(params)

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    if not enqueue((cmd, future)):
        return {"error": "Queue Full - request dropped"}

    return await future
