import asyncio, time
from config import RATE_LIMIT

class RateLimiter:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.rate_per_sec = RATE_LIMIT
            cls._instance.last_request = 0
        return cls._instance

    async def acquire(self):
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < 1 / self.rate_per_sec:
            await asyncio.sleep(1 / self.rate_per_sec - elapsed)
        self.last_request = time.time()
