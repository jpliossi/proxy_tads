from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import proxy, metrics, health
from core.worker import start_worker

# Lifespan: substitui os eventos de startup/shutdown antigos
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que era executado no "startup"
    start_worker()
    print("Aplicação iniciando...")
    yield
    # Código que seria executado no "shutdown" (opcional)
    print("Aplicação finalizando...")

# Cria a instância do FastAPI usando lifespan
app = FastAPI(lifespan=lifespan)

# Inclui as rotas do seu projeto
app.include_router(proxy.router)
app.include_router(metrics.router)
app.include_router(health.router)

# Exemplo de rota simples (opcional)
@app.get("/")
async def root():
    return {"message": "Proxy Service rodando!"}
