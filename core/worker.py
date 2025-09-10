import asyncio
from core.queue_manager import dequeue
from core.rate_limiter import RateLimiter

rate_limiter = RateLimiter()

async def worker():
    while True:
        item = dequeue()
        if item:
            cmd, future = item
            await rate_limiter.acquire()
            try:
                result = await cmd.execute()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
        await asyncio.sleep(0.01)

def start_worker():
    asyncio.create_task(worker())
