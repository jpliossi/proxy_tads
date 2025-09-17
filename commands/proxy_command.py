import httpx
from config import UPSTREAM_URL

class ProxyCommand:
    def __init__(self, params: dict, headers: dict):
        self.params = params
        self.headers = headers

    async def execute(self):
        async with httpx.AsyncClient() as client:
            resp = await client.get(UPSTREAM_URL, params=self.params, headers=self.headers)
            try:
                return resp.json()
            except ValueError:
                return {"response_text": resp.text}
