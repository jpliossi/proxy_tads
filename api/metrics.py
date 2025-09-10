from fastapi import APIRouter
from core.queue_manager import queue
from core.rate_limiter import RateLimiter

router = APIRouter()

@router.get("/metrics")
async def metrics():
    rl = RateLimiter()
    return {
        "queue_length": len(queue),
        "last_request_time": rl.last_request
    }
