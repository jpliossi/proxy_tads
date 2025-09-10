import httpx
from config import UPSTREAM_URL

class ProxyCommand:
    def __init__(self, params):
        self.params = params

    async def execute(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(UPSTREAM_URL, params=self.params)
            return resp.json()
