import asyncio
from core.queue_manager import dequeue

async def worker_loop():
    while True:
        item = dequeue()
        if item:
            cmd, future = item
            result = await cmd.execute()
            future.set_result(result)
        else:
            await asyncio.sleep(0.1)  # evita busy loop

def start_worker():
    loop = asyncio.get_event_loop()
    loop.create_task(worker_loop())
