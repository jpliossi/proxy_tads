from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import proxy
from core.worker import start_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_worker()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(proxy.router)
