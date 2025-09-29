import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from collections import defaultdict

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

UPSTREAM_URL = "https://score.hsborges.dev/api/score"  # ajuste se necessário
MAX_CALLS_PER_SECOND = 1  # apenas 1 chamada por segundo
PENALTY_SECONDS = 2       # penalidade ao violar o limite
CACHE_TTL = 60            # TTL do cache (em segundos)
REQUEST_QUEUE_MAXSIZE = 1000  # fila máxima

class Cache:
    def __init__(self):
        self.store: Dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self.store:
                value, exp = self.store[key]
                if datetime.utcnow().timestamp() < exp:
                    return value
                else:
                    del self.store[key]
            return None

    async def set(self, key: str, value: Any, ttl: int = CACHE_TTL):
        async with self._lock:
            self.store[key] = (value, datetime.utcnow().timestamp() + ttl)

    async def dump(self):
        async with self._lock:
            return {
                k: {
                    "value": v[0],
                    "expires_at": datetime.utcfromtimestamp(v[1]).isoformat()
                }
                for k, v in self.store.items()
            }

cache = Cache()

@dataclass
class QueueItem:
    key: str
    params: Dict[str, Any]
    headers: Dict[str, str]

request_queue: "asyncio.Queue[QueueItem]" = asyncio.Queue(maxsize=REQUEST_QUEUE_MAXSIZE)
in_flight: Dict[str, List[asyncio.Future]] = defaultdict(list)
in_flight_lock = asyncio.Lock()
httpx_client: Optional[httpx.AsyncClient] = None

last_request_time: Optional[float] = None

async def scheduler_worker():
    global last_request_time
    print("[WORKER] Iniciado")
    delay = 1.0 / MAX_CALLS_PER_SECOND

    while True:
        item: QueueItem = await request_queue.get()
        now = datetime.utcnow().timestamp()

        # Penalidade se o intervalo for muito curto
        if last_request_time and now - last_request_time < delay:
            print(f"[RATE LIMIT] Violado para {item.key}, penalidade {PENALTY_SECONDS}s")
            await asyncio.sleep(PENALTY_SECONDS)

        last_request_time = datetime.utcnow().timestamp()

        # 1. Tenta cache
        cached = await cache.get(item.key)
        if cached is not None:
            print(f"[CACHE HIT] {item.key}")
            async with in_flight_lock:
                futures = in_flight.pop(item.key, [])
            for fut in futures:
                if not fut.done():
                    fut.set_result(cached)
            request_queue.task_done()
            await asyncio.sleep(delay)
            continue

        # 2. Chamada ao upstream
        try:
            resp = await httpx_client.get(UPSTREAM_URL, params=item.params, headers=item.headers)
            resp.raise_for_status()
            content = resp.json()
        except Exception as e:
            content = {"error": f"{type(e).__name__}: {str(e)}"}
            print(f"[ERRO PROXY] {item.key} -> {content['error']}")

        # 3. Cacheia e resolve futuros
        await cache.set(item.key, content)
        async with in_flight_lock:
            futures = in_flight.pop(item.key, [])
        for fut in futures:
            if not fut.done():
                fut.set_result(content)

        request_queue.task_done()
        await asyncio.sleep(delay)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global httpx_client
    httpx_client = httpx.AsyncClient(timeout=10.0)
    asyncio.create_task(scheduler_worker())
    yield
    await httpx_client.aclose()

app = FastAPI(title="Proxy com Fila, Scheduler, Deduplicação e Cache", lifespan=lifespan)

class ScoreResponse(BaseModel):
    score: Optional[Any] = None
    error: Optional[str] = None

@app.get("/api/score", response_model=ScoreResponse)
async def proxy_score(cpf: str, client_id: str):
    key = f"{cpf}:{client_id}"

    # cache imediato
    cached = await cache.get(key)
    if cached is not None:
        return cached

    fut = asyncio.get_event_loop().create_future()
    async with in_flight_lock:
        if key in in_flight and len(in_flight[key]) > 0:
            in_flight[key].append(fut)
            result = await fut
            return result
        else:
            in_flight[key].append(fut)

    params = {"cpf": cpf}
    headers = {"client-id": client_id}
    item = QueueItem(key=key, params=params, headers=headers)

    try:
        request_queue.put_nowait(item)
    except asyncio.QueueFull:
        async with in_flight_lock:
            try:
                in_flight[key].remove(fut)
                if not in_flight[key]:
                    del in_flight[key]
            except ValueError:
                pass
        raise HTTPException(status_code=503, detail="Fila cheia - tente novamente mais tarde")

    result = await fut

    async with in_flight_lock:
        try:
            in_flight[key].remove(fut)
            if not in_flight[key]:
                del in_flight[key]
        except (KeyError, ValueError):
            pass

    return result

@app.get("/_debug/cache")
async def debug_cache():
    data = await cache.dump()
    return {"cache": data, "size": len(data)}
